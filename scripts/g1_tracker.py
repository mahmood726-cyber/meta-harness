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
import re
import os
import re
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
                           events_c=primary.get("events_c"), n_c=primary.get("n_c"), mean_t=primary.get("mean_t"),
                           sd_t=primary.get("sd_t"), mean_c=primary.get("mean_c"), sd_c=primary.get("sd_c"))


def row_value(r):
    """A SecondaryRow as the value dict agreement() compares (None for no row)."""
    if r is None:
        return None
    return {k: getattr(r, k, None) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")}


def agreement(ours, theirs):
    """Our pooled value vs the comparator's printed row for the same trial: AGREE / DISAGREE / NOT_COMPARABLE[:why]."""
    if not ours or not theirs:
        return "NOT_COMPARABLE:NO_COMPARATOR_ROW" if ours else "NOT_COMPARABLE"
    # two 2x2 tables compare as counts when both sides label a COUNT-derived ratio (RR / OR): the counts carry no
    # measure. Never across an HR (a time-to-event row's counts are not its estimate's data)
    if ours.get("events_t") is not None and theirs.events_t is not None and \
            {(ours.get("measure") or "").upper(), (theirs.measure or "").upper()} <= {"RR", "OR"}:
        same = (ours["events_t"], ours["n_t"], ours["events_c"], ours["n_c"]) == \
               (theirs.events_t, theirs.n_t, theirs.events_c, theirs.n_c)
        return "AGREE" if same else "DISAGREE"
    if (ours.get("measure") or "").upper() and theirs.measure and (ours.get("measure") or "").upper() != theirs.measure.upper():
        return f"NOT_COMPARABLE:{ours.get('measure')}_VS_{theirs.measure}"
    if ours.get("events_t") is not None and theirs.events_t is not None:
        same = (ours["events_t"], ours["n_t"], ours["events_c"], ours["n_c"]) == \
               (theirs.events_t, theirs.n_t, theirs.events_c, theirs.n_c)
        return "AGREE" if same else "DISAGREE"
    if ours.get("effect") is None and ours.get("events_t") is not None and theirs.effect is not None             and theirs.measure.upper() in ("RR", "OR"):
        # our 2x2 vs their printed ratio: the ratio our counts imply, compared with their POINT at their precision
        a, n1, c, n2 = ours["events_t"], ours["n_t"], ours["events_c"], ours["n_c"]
        if min(n1, n2) > 0 and a > 0 and c > 0 and a < n1 and c < n2:
            r = (a / n1) / (c / n2) if theirs.measure.upper() == "RR" else (a / (n1 - a)) / (c / (n2 - c))
            return "AGREE_ON_POINT" if sm._eq_printed(f"{r:.6f}", theirs.effect) else                 f"DISAGREE:our_counts_imply_{r:.2f}_vs_printed_{theirs.effect}"
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
    raw = {}
    for side, idx in (("ours", 0), ("theirs", 1)):
        yv = [sm.row_yi_vi(p[idx]) for p in pairs]
        if any(v is None for v in yv):
            return {"state": f"{side.upper()}_ROW_NOT_POOLABLE", "k": len(pairs)}
        mu, lo, hi = (g(x) for x in sm.pool([v[0] for v in yv], [v[1] for v in yv], method, hk))
        raw[side] = {"estimate": float(mu), "ci_low": float(lo), "ci_high": float(hi)}
        out[side] = {k: round(v, 4) for k, v in raw[side].items()}
    out["verdict"] = result_verdict(raw["ours"], raw["theirs"], measure)     # decided UNROUNDED; displayed rounded
    return out


def whole_pool_event_check(o):
    """For whole pools that cannot be compared on one measure: does the comparator's printed outcome even count the
    trials' primary outcome? (harness/event_total_check.py: the trials' summed primary-outcome events, each a verbatim
    span of the trial's held abstract, against the most events the comparator's printed rates allow over its stated
    patients.) EVENTS_INCOMPATIBLE_WITH_COMPARATOR_RATES means no number on our side could 'agree' with it -- the
    comparator counted a different outcome definition, window or population. Read-only; never changes the verdict."""
    try:
        from harness import comparator_membership as cmb, event_total_check as etc
        slug = o.get("slug")
        crec = held_record(slug, o.get("comparator_pmid")) or {}
        st = cmb.stated_trial_count(crec.get("abstract") or "")
        cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
        terms = [(cfg.get("comparator_outcomes") or [{}])[0].get("name") or ""] + \
                list((cfg.get("primary_outcome") or {}).get("keywords") or [])
        matched = [str(x.get("family") or "").replace("PMID ", "").strip() for x in o.get("trials") or [] if is_matched(x)]
        return etc.check(crec.get("abstract") or "", terms, (st or {}).get("n_patients"),
                         {p: (held_record(slug, p) or {}).get("abstract") or "" for p in matched})
    except Exception as e:                                  # an unrunnable check reports that it did not run
        return {"state": "NOT_RUN", "why": str(e)[:200]}


def pair_trial(pair, trials):
    """The tracker trial a same-trials pair belongs to: the trial whose comparator_row has the comparator side's printed
    values (effect, lower, upper -- the same row object's numbers); else one whose label equals either side's label."""
    o, t = pair
    for x in trials or []:
        cr = x.get("comparator_row") or {}
        if cr and all(str(cr.get(k)) == str(getattr(t, k, None)) for k in ("effect", "lower", "upper")):
            return x
    return next((x for x in trials or [] if x.get("label") in (o.trial_label, t.trial_label)), None)


def verdict_attribution(pairs, method_label, trials=()):
    """WHICH shared trial makes the two same-trial pools disagree -- per trial, typed. For each shared trial i, the pools
    are recomputed with ONLY trial i's row taken from the other side (same method, same verdict rule, same_trials_pool):
      theirs_with_our_row_i  -- the comparator's pool with our value for trial i
      ours_with_their_row_i  -- our pool with the comparator's value for trial i
    A trial is a DRIVER when either swap alone turns the verdict to AGREE (or to the same conclusion). Every trial's own
    row agreement and, where the tracker attributed it, its analysis-set finding are carried beside it, so the
    disagreement is closed trial by trial rather than as one number. Read-only: nothing is pooled differently."""
    if len(pairs) < 2:
        return None
    by_label = {x.get("label"): x for x in trials or []}
    out = []
    for i, (o_i, t_i) in enumerate(pairs):
        swapped_t = [(o, (o_i if j == i else t)) for j, (o, t) in enumerate(pairs)]
        swapped_o = [((t_i if j == i else o), t) for j, (o, t) in enumerate(pairs)]
        a, b = same_trials_pool(swapped_t, method_label), same_trials_pool(swapped_o, method_label)

        def conc(r, side):
            if r.get("state") != "POOLED":
                return None
            v = r["verdict"]
            return v.get("conclusion") or v.get(side)
        x = pair_trial((o_i, t_i), trials) or {}
        lab = x.get("label") or t_i.trial_label or o_i.trial_label
        flips = {"theirs_with_our_row": (a.get("verdict") or {}).get("verdict"),
                 "theirs_with_our_row_conclusion": conc(a, "theirs"), "theirs_with_our_row_pool": a.get("theirs"),
                 "ours_with_their_row": (b.get("verdict") or {}).get("verdict"),
                 "ours_with_their_row_conclusion": conc(b, "ours"), "ours_with_their_row_pool": b.get("ours")}
        driver = any(str(flips[k] or "").startswith(("AGREE", "SAME_CONCLUSION")) for k in ("theirs_with_our_row",
                                                                                             "ours_with_their_row"))
        out.append({"trial": lab, "row_agreement": x.get("agreement_with_comparator_row"),
                    "analysis_set": (x.get("analysis_set_attribution") or {}).get("state"),
                    "comparator_row_nearest_set": (x.get("analysis_set_attribution") or {}).get("nearest"),
                    "disagreement_side": x.get("disagreement_side"), "driver": driver, **flips})
    drivers = [r["trial"] for r in out if r["driver"]]
    closed = bool(drivers) and all(r["row_agreement"] and (r["driver"] or str(r["row_agreement"]).startswith("AGREE"))
                                   for r in out)
    drv = [r for r in out if r["driver"]]
    # RESOLUTION: the disagreement is RESOLVED AGAINST THE COMPARATOR'S ROW when every driver's row is the comparator's
    # error (SECONDARY_WRONG: our number is anchored in the trial's own report span, theirs is not) and the comparator's
    # pool with the trial's own number AGREES with ours. Anything less stays UNRESOLVED. RESULT_AGREES is not changed:
    # the numbers do differ; this says why, and on whose side.
    if closed and drv and all(str(r["disagreement_side"] or "").startswith("SECONDARY_WRONG")
                              and str(r["theirs_with_our_row"] or "").startswith("AGREE") for r in drv):
        resolution = {"state": "RESOLVED_AGAINST_COMPARATOR_ROW", "rows": [r["trial"] for r in drv],
                      "why": "every driver is a comparator row the trial's own report does not support "
                             "(SECONDARY_WRONG); with the trial's own number the comparator's pool agrees with ours"}
    else:
        resolution = {"state": "UNRESOLVED", "rows": [r["trial"] for r in drv],
                      "why": "a driver's side is undetermined, or swapping drivers does not reach agreement"}
    return {"basis": "single-trial swaps of the same-trials pools (same method, same verdict rule)",
            "drivers": drivers, "per_trial": out, "closed": closed, "resolution": resolution}


_COUNT_MEASURES = ("RR", "OR")


def on_comparator_measure(ours, theirs):
    """OUR trial row expressed in the COMPARATOR'S measure, or (None, why). Same measure: as is. The comparator pooled
    RR / OR and our verified row carries ARM COUNTS: re-expressed from the counts (the 2x2 carries no measure). An HR
    is NEVER converted to a ratio of risks: that pair is a MEASURE_DIFFERENCE (typed, named, never a failure alone)."""
    om, tm = (ours.measure or "").upper(), (theirs.measure or "").upper()
    if om == tm or not tm:
        return ours, None
    counts = None not in (ours.events_t, ours.n_t, ours.events_c, ours.n_c)
    if tm in _COUNT_MEASURES and counts and om in ("", "RR", "OR"):
        return sm.SecondaryRow(meta_pmid=ours.meta_pmid, meta_doi="", location={}, source_digest="", provenance=ours.provenance,
                               trial_label=ours.trial_label, measure=tm, outcome_definition="",
                               events_t=ours.events_t, n_t=ours.n_t, events_c=ours.events_c, n_c=ours.n_c), None
    return None, f"MEASURE_DIFFERENCE:{om or '?'}_VS_{tm}"


def _est(row):
    """(estimate, ci_low, ci_high) of one row on its own scale, from its effect + CI or its counts."""
    yv = sm.row_yi_vi(row)
    if yv is None:
        return None
    g = math.exp if (row.measure or "").upper() in sm.RATIO else (lambda x: x)
    se = math.sqrt(yv[1])
    return {"estimate": g(yv[0]), "ci_low": g(yv[0] - 1.959963984540054 * se), "ci_high": g(yv[0] + 1.959963984540054 * se)} \
        if row.effect is None else {"estimate": sm._num(row.effect), "ci_low": sm._num(row.lower), "ci_high": sm._num(row.upper)}


def _concl(r, measure):
    null = 1.0 if measure in sm.RATIO else 0.0
    return "BENEFIT" if r["ci_high"] < null else "HARM" if r["ci_low"] > null else "NULL_INCLUDED"


def same_trials_compare(pairs, method_label):
    """The same-trials comparison ON THE COMPARATOR'S MEASURE (5 Oct class):
      >= 2 comparable pairs   both sides pooled by ONE method on the comparator's measure (same_trials_pool)
      exactly 1 shared trial  ONE_SHARED_TRIAL: that trial compared directly (k = 1 rule)
      1 comparable + others   that trial's verdict, the others as measure differences
      only measure differences  MEASURE_DIFFERENCE: our HR vs their RR/OR is never converted; it passes only on the
                              SAME CONCLUSION about the null (per pair, and pooled when both sides pool)
    Every measure-difference pair is listed (trial, both values, both conclusions)."""
    comp, md = [], []
    for o_, t_ in pairs:
        row, why = on_comparator_measure(o_, t_)
        if row is not None:
            comp.append((row, t_))
            continue
        eo, et = _est(o_), _est(t_)
        if eo is None or et is None:
            continue
        md.append({"trial": t_.trial_label or o_.trial_label, "why": why,
                   "ours": {"measure": o_.measure, **{k: round(v, 4) for k, v in eo.items()}},
                   "theirs": {"measure": t_.measure, **{k: round(v, 4) for k, v in et.items()}},
                   "same_conclusion": _concl(eo, (o_.measure or "").upper()) == _concl(et, (t_.measure or "").upper())})
    md_ok = all(d["same_conclusion"] for d in md)
    if len(comp) >= 2:
        out = same_trials_pool(comp, method_label)
    elif len(comp) == 1:
        o_, t_ = comp[0]
        eo, et = _est(o_), _est(t_)
        m = (t_.measure or "").upper()
        out = ({"state": "ONE_SHARED_TRIAL" if not md else "ONE_COMPARABLE_TRIAL", "k": 1, "measure": m,
                "trial": t_.trial_label, "ours": {k: round(v, 4) for k, v in eo.items()}, "theirs": et,
                "verdict": result_verdict(eo, et, m)} if eo and et else {"state": "ROW_NOT_COMPARABLE", "k": 1})
    elif md:
        out = {"state": "MEASURE_DIFFERENCE", "k": len(md)}
        same = md_ok
        ours_m = {(p[0].measure or "").upper() for p in pairs}
        theirs_m = {(p[1].measure or "").upper() for p in pairs}
        if len(pairs) >= 2 and len(ours_m) == 1 and len(theirs_m) == 1:
            method, hk = method_label.replace("+HK", ""), method_label.endswith("+HK")
            pooled = {}
            for side, idx, ms_ in (("ours", 0, ours_m), ("theirs", 1, theirs_m)):
                yv = [sm.row_yi_vi(p[idx]) for p in pairs]
                if any(v is None for v in yv):
                    pooled = {}
                    break
                g = math.exp if next(iter(ms_)) in sm.RATIO else (lambda x: x)
                mu, lo, hi = (g(x) for x in sm.pool([v[0] for v in yv], [v[1] for v in yv], method, hk))
                pooled[side] = {"measure": next(iter(ms_)), "estimate": round(float(mu), 4), "ci_low": round(float(lo), 4),
                                "ci_high": round(float(hi), 4)}
            if pooled:
                out.update(pooled)
                same = same and _concl(pooled["ours"], pooled["ours"]["measure"]) == _concl(pooled["theirs"], pooled["theirs"]["measure"])
        out["verdict"] = {"verdict": "MEASURE_DIFFERENCE_SAME_CONCLUSION" if same else "DIFFERENT_CONCLUSION",
                          "basis": "our verified values are HRs; the comparator pooled a ratio of risks/odds: never converted"}
    else:
        return same_trials_pool(pairs, method_label)
    if md:
        out["measure_differences"] = md
        v = (out.get("verdict") or {}).get("verdict")
        if v == "AGREE" and not md_ok:
            out["verdict"] = dict(out["verdict"], verdict="DIFFERENT_CONCLUSION",
                                  why="a measure-difference pair reaches another conclusion about the null")
    return out


_NUMW = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15}
_KTRIALS = re.compile(r"(?<![Pp]hase )(?<![Pp]hase)\b(\d{1,3}|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)\s+"
                      r"(?:(?:phase\s*(?:3|iii)|large|randomi[sz]ed|controlled|clinical|placebo-controlled|double-blind)\s+)*"
                      r"(?:trials|studies|rcts)\b", re.I)


def printed_trial_count(text):
    """k as the comparator's own text states it ('6 phase 3 trials', 'Four randomized controlled trials'), only when
    the text states exactly ONE such count (a screened-records count beside it is ambiguity, never a pick)."""
    ks = {(_NUMW.get(m.group(1).lower()) or int(m.group(1))) for m in _KTRIALS.finditer(text or "")
          if m.group(1).lower() in _NUMW or m.group(1).isdigit()}
    return ks.pop() if len(ks) == 1 else None


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


_STOP = {"of", "for", "the", "and", "or", "with", "in", "to", "a", "due", "by"}


def _name_words(x):
    """Content words of an outcome name or registry title, plural and British -isation folded, and the registry's 'HF'
    read as 'heart failure' (AFFIRM-AHF NCT02937454 posts 'HF Hospitalisations' in participants: never named)."""
    import re as _r
    w = _r.findall(r"[a-z]+", (x or "").lower().replace("hospitalis", "hospitaliz"))
    w = [y for v in w for y in (("heart", "failure") if v == "hf" else (v,))]
    return {_r.sub(r"s$", "", v) for v in w if v not in _STOP}


_KW_STOP = {"or", "and", "an", "a", "the", "for", "of", "to", "with", "in", "on", "at", "by", "due"}


def _kw_tokens(x):
    x = (x or "").lower()
    x = re.sub(r"\bcv\b", "cardiovascular", x)
    x = re.sub(r"\bhf\b", "heart failure", x)
    x = re.sub(r"hospitalisation", "hospitalization", x)
    x = re.sub(r"\bdue to\b", "for", x)
    return [w for w in re.findall(r"[a-z0-9]+", x) if w not in _KW_STOP]


def keyword_named(keyword, title):
    """Does a registry outcome TITLE name this topic keyword? Literally, or in its own wording: after normalising
    abbreviations / spellings ('CV' = cardiovascular, 'Due to' = for), EVERY content word of the keyword is in the
    title (DELIVER: 'CV Death, Hospitalization Due to Heart Failure or Urgent Visit ...'). A generic anchor ('primary
    outcome') never names; a component-only title cannot contain a composite keyword's words."""
    from harness import extract
    k = (keyword or "").lower().strip()
    if not k or k in extract.GENERIC_ANCHORS:
        return False
    if k in (title or "").lower():
        return True
    kt, tt = _kw_tokens(k), set(_kw_tokens(title))
    return len(kt) >= 2 and all(w in tt for w in kt)


_PER_PROTOCOL = re.compile(r"\bper[- ]protocol\b|\bPP (?:population|set|analysis)\b", re.I)
_EXTENDED_COMPOSITE = re.compile(r"\bplus\b|\bexpanded\b|\bextended\b|\b(?:4|four|5|five)[- ]point\b", re.I)
_THREE_POINT = re.compile(r"\b(?:3|three)[- ]point\b", re.I)
_RECURRENT = re.compile(r"\brecurrent\b|\btotal (?:number of )?(?:events|hospitali[sz]ations)\b|first and subsequent", re.I)
_DEATH = re.compile(r"\bdeaths?\b|\bmortality\b|\bdied\b|\bfatal\b", re.I)
# a protocol outcome that is itself a set of events ('Major vascular events' includes vascular death; not flagged composite)
_EVENTS_SPEC = re.compile(r"\bevents?\b|composite|\bMACE\b", re.I)


def analysis_set_or_extension_differs(spec_name, title, population):
    """A registry outcome that names our outcome but is ANOTHER analysis set or an EXTENDED composite (dpp4 TECOS
    NCT00790205 posts 'MACE Plus' -- its 4-point composite -- and '(Per Protocol Population)' beside the ITT 3-point
    MACE; both reached the ARMS gate and only the missing counts refused them). None when neither applies."""
    t = title or ""
    pop = (population or "").lower()
    if _PER_PROTOCOL.search(t) and ("intention" in pop or "itt" in pop.split() or "all randomi" in pop):
        return f"analysis set: the registry outcome is per-protocol ('{t}'); the protocol's population is '{population}'"
    if _THREE_POINT.search(spec_name or "") and _EXTENDED_COMPOSITE.search(t):
        return f"extended composite: the registry outcome '{t}' extends the protocol's '{spec_name}'"
    # first AND recurrent events (a total-events analysis) is not time to the first event (sglt2-pp EMPEROR-Preserved:
    # 'Occurrence of Adjudicated Hospitalisation for Heart Failure (HHF) (First and Recurrent)')
    if _RECURRENT.search(t) and not _RECURRENT.search(spec_name or ""):
        return f"recurrent-event analysis: the registry outcome '{t}' counts recurrent events; the protocol's is first event"
    # a protocol outcome without death, a registry outcome that adds it ('HF Hospitalizations and CV Death', AFFIRM-AHF):
    # a different composite even when no 'composite' / 'or' word says so
    from harness import extract
    single = not extract.declared_is_composite(spec_name or "") and not _EVENTS_SPEC.search(spec_name or "")
    if single and _DEATH.search(t) and not _DEATH.search(spec_name or ""):
        return f"composite with death: the registry outcome '{t}' adds death to the protocol's '{spec_name}'"
    return None


def binding_verdict(spec_name, keywords, title, n_groups, is_primary=False, analysis=None, estimand=None,
                    population=None):
    """One registry outcome through the binding gates, in order:
      OUTCOME_NOT_NAMED  the title names no topic keyword (generic anchors like 'primary outcome' do not count): being
                         the trial's PRIMARY outcome is not identity with OUR outcome
      ESTIMAND           a different composite: extract.composite_component_mismatch on the title as a definition, or a
                         composite title for a declared SINGLE outcome ('Death or Mechanical Ventilation' is not mortality)
      ARMS               fewer than two result groups with people-unit counts"""
    from harness import extract
    t = (title or "").lower()
    named = [k for k in keywords if keyword_named(k, title)]
    # ...or the topic's OWN outcome NAME, when every content word of it (plural / British spelling folded) is in the
    # title: iv-iron's keywords all say 'worsening', so HEART-FID's primary 'Number of Hospitalizations for Heart
    # Failure' (the topic's 'Heart-failure hospitalization') was never named. Corpus: 2 candidates newly named --
    # HEART-FID, and DAPA-HF's composite, which the ESTIMAND gate below still refuses.
    if not named and spec_name and _name_words(spec_name) and _name_words(spec_name) <= _name_words(title):
        named = [spec_name]
    if not named:
        return {"gate": "OUTCOME_NOT_NAMED", "verdict": "REFUSED",
                "reason": "registry title names none of the topic's outcome keywords" + (" (it is the trial's PRIMARY "
                                                                                       "outcome)" if is_primary else "")}
    mm = definition_gate(spec_name, title)
    if not mm and not extract.declared_is_composite(spec_name) and extract._names_composite(title):
        mm = f"declared single outcome '{spec_name}' but the registry outcome is a composite: '{title}'"
    if not mm:
        mm = analysis_set_or_extension_differs(spec_name, title, population)
    if mm:
        return {"gate": "ESTIMAND", "verdict": "REFUSED", "reason": mm, "named_by": named}
    if n_groups < 2:
        # an effect ESTIMAND needs no arm counts: the registry's own analysis between exactly two groups, on the
        # protocol's measure, with BOTH CI bounds, is its result (dpp4 TECOS NCT00790205: 'First Confirmed CV Event of
        # MACE (Intent to Treat Population)', HR 0.99 (0.89, 1.1), refused for lacking people-unit counts). A one-sided
        # bound is no CI (EXAMINE NCT00968708: HR 0.962, upper 1.16 only) and is refused AS such.
        ok, why = posted_effect_on_estimand(analysis, estimand)
        if ok:
            return {"gate": None, "verdict": "BINDABLE", "reason": None, "named_by": named,
                    "basis": "POSTED_EFFECT_ON_PROTOCOL_ESTIMAND"}
        return {"gate": "ARMS", "verdict": "REFUSED", "named_by": named,
                "reason": why or "fewer than two result groups with people-unit counts"}
    return {"gate": None, "verdict": "BINDABLE", "reason": None, "named_by": named}


_PARAM_OF = {"HR": "hazard ratio", "RR": "risk ratio", "OR": "odds ratio", "MD": "mean difference"}


def posted_effect_on_estimand(analysis, estimand):
    """(True, None) when a posted analysis is the protocol's estimand between two groups with a two-sided CI;
    (False, reason) when it is the estimand but not usable as such; (False, None) when it says nothing."""
    want = _PARAM_OF.get((estimand or "").upper())
    if not (want and analysis and want in (analysis.get("param_type") or "").lower()):
        return False, None
    if len(set(analysis.get("groups") or [])) != 2:
        return False, f"posted {analysis.get('param_type')} is not between exactly two groups"
    vals = [sm._num(analysis.get(k)) for k in ("param_value", "ci_lower", "ci_upper")]
    if None in vals:
        return False, (f"posted {analysis.get('param_type')} {analysis.get('param_value')} has a one-sided bound only "
                       f"(lower '{analysis.get('ci_lower')}', upper '{analysis.get('ci_upper')}'): no two-sided CI")
    lo, pt, hi = vals[1], vals[0], vals[2]
    if not lo < pt < hi:
        return False, f"posted {analysis.get('param_type')} {pt} lies outside its CI ({lo}, {hi})"
    return True, None


def binding_candidate(title, keywords, is_primary):
    """A posted outcome is examined when it is the trial's PRIMARY outcome or its title names a topic keyword -- in the
    registry's own wording, by the SAME rule as the gate (keyword_named): the candidate filter matched literal
    substrings only, so 'Mortality Rate at Day 28' was never a candidate for 'mortality at day 28' (tocilizumab)."""
    return bool(is_primary) or any(keyword_named(k, title) for k in keywords or [])


def registry_binding(nct, spec_name, keywords, estimand=None, population=None):
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
    sw = _name_words(spec_name)
    cands = []
    for oid, o in reg["outcomes"].items():
        t = o.get("title") or ""
        # a candidate is named the SAME way the binding gate names it: the trial's PRIMARY, a keyword in the registry's own
        # wording (acq/k-gap binding_candidate: 'Mortality Rate at Day 28', tocilizumab), OR the topic's outcome name
        # (AFFIRM-AHF 'HF Hospitalisations') -- consolidated 2026-10-05
        if (not binding_candidate(t, keywords, (o.get("type") or "").upper() == "PRIMARY")
                and not (sw and sw <= _name_words(t))):
            continue
        groups = reg["groups"].get(oid) or []
        an = next((a for a in reg["analyses"] if a["outcome_id"] == oid), None)
        c = {"nct": nct, "outcome_id": oid, "title": t, "time_frame": o.get("time_frame"),
             "arms": [dict(g, title=reg["group_titles"].get(str(g["group"]))) for g in groups], "analysis": an,
             "snapshot": reg["_snapshot"]}
        c.update(binding_verdict(spec_name, keywords, t, len({g["group"] for g in groups}),
                                 is_primary=(o.get("type") or "").upper() == "PRIMARY", analysis=an, estimand=estimand,
                                 population=population))
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


def protocol_rule_for(cfg, rule_id, reason):
    """The REGISTERED protocol field a screen exclusion applied (harness/screen.py), cited as 'include.<field>[i] = ...'.
      X1        the protocol's randomised-controlled-trial requirement
      X2        include.population_none[i] (a named excluded population) / include.population_any (none met)
      X3        include.intervention_none[i] (wrong form) / include.intervention_any / include.comparator_any
      X-DESIGN  include.design_none[i] / include.design_double_blind / include.design_any"""
    import re as _re
    inc = cfg.get("include") or {}
    m = _re.search(r"(?:mention|mentions|matches excluded) '([^']+)'", reason or "")
    term = m.group(1) if m else None
    if rule_id == "X1":
        return "protocol design: randomised controlled trials only (harness/screen.py X1)"
    if rule_id == "X2":
        return protocol_rule(cfg, term) if term else f"include.population_any = {inc.get('population_any')!r} (none met)"
    if rule_id == "X3":
        if "wrong form" in (reason or "") and term:
            return protocol_rule(cfg, term)
        if "comparator" in (reason or ""):
            return f"include.comparator_any = {inc.get('comparator_any')!r} (none met)"
        return f"include.intervention_any = {inc.get('intervention_any')!r} (none met)"
    if rule_id == "X-DESIGN":
        if term:
            return protocol_rule(cfg, term)
        if "double-blind" in (reason or ""):
            return f"include.design_double_blind = {inc.get('design_double_blind')!r}"
        return f"include.design_any = {inc.get('design_any')!r} (none met)"
    return None


_AUDIT = None


def exclusion_audit_class(slug, pmid):
    """The deterministic exclusion audit's class for a seeded exclusion (scripts/k_gap_exclusion_audit.py):
    TRUE_SCOPE_DIFFERENCE / SCREENER_ERROR / INSUFFICIENT_RECORD / INCONSISTENT, or None when not audited."""
    global _AUDIT
    if _AUDIT is None:
        ap = os.path.join(OUT, "exclusion_audit.json")
        _AUDIT = {}
        for r in (_j(ap).get("rows") or []) if os.path.exists(ap) else []:
            _AUDIT.setdefault((r.get("slug"), str(r.get("pmid"))), r)
    r = _AUDIT.get((slug, str(pmid)))
    if r and r.get("class") == "INSUFFICIENT_RECORD":
        # the record lacked the fact; the committed FULL-TEXT pass (scripts/k_gap_exclusion_fulltext.py: regex on the held
        # OA full text first, a verified recorded reader second) may have resolved it -- its class decides then
        ft = _ft_resolution(slug, pmid)
        if ft:
            return ft
    return (r.get("class"), r.get("subclass")) if r else (None, None)


_FT = None


def _ft_resolution(slug, pmid):
    global _FT
    if _FT is None:
        fp = os.path.join(OUT, "exclusion_fulltext.json")
        _FT = {(x.get("slug"), str(x.get("pmid"))): x for x in ((_j(fp).get("rows") or []) if os.path.exists(fp) else [])}
    x = _FT.get((slug, str(pmid)))
    # only a DETERMINISTIC resolution (regex on the held full text) decides; a recorded model reader's verdict stays a
    # PROPOSAL (lane rule: recorded model calls only as proposals) and leaves the item an open, insufficient-record gap
    if x and x.get("class_after") in ("TRUE_SCOPE_DIFFERENCE", "SCREENER_ERROR") and \
            str(x.get("how") or "").startswith("REGEX_ON_FULLTEXT"):
        return x["class_after"], f"{x.get('subclass_after') or x.get('reader_agreement') or ''} [full text: {x.get('how')}]"
    return None


def exclusion_audit_span(slug, pmid):
    """The audit's SPAN for a TRUE_SCOPE_DIFFERENCE: the record's own words establishing the excluding fact. When the
    record was insufficient and the committed full-text pass resolved it by REGEX, the span is the full text's words
    (field 'fulltext', with the sha256 of the held body it was read from)."""
    exclusion_audit_class(slug, pmid)
    r = _AUDIT.get((slug, str(pmid))) or {}
    if r.get("class") == "TRUE_SCOPE_DIFFERENCE":
        return r.get("span")
    if r.get("class") == "INSUFFICIENT_RECORD" and _ft_resolution(slug, pmid):
        x = _FT.get((slug, str(pmid))) or {}
        if x.get("class_after") == "TRUE_SCOPE_DIFFERENCE" and x.get("span"):
            return dict(x["span"], fulltext_sha256=x.get("fulltext_sha256"), fulltext_source=x.get("fulltext"))
    return None


def held_fulltext(pmid, sha256, source=None, slug=None):
    """The held OA full text the full-text pass read (gitignored: outputs/k_gap/_ft for PMC_OA, outputs/k_gap/_upw for
    UNPAYWALL_OA), cut to the prefix it read, ONLY when its sha256 is the one recorded; otherwise None. Offline only:
    never re-fetched here; a clone without the body cannot verify, so the span is not verified."""
    import hashlib
    import k_gap_counterfactual as cfm
    import k_gap_exclusion_fulltext as eft
    try:
        if source == "UNPAYWALL_OA":
            from kgap import k_gap
            doi = (held_record(slug, pmid) or {}).get("doi") if slug else None
            ft = (k_gap.unpaywall_text(doi, os.path.join(OUT, "_upw"), os.path.join(OUT, "unpaywall_text_index.json"),
                                       offline=True).get("text") or "") if doi else ""
        else:
            ft = cfm.pmc_fulltext_cached(str(pmid), offline=True) or ""
    except Exception:                                    # no body in this clone: unverifiable here, so not verified
        return None
    ft = ft[:eft.FT_CAP]
    return ft if ft and hashlib.sha256(ft.encode("utf-8")).hexdigest() == sha256 else None


def span_source_of(slug, pmid, sp):
    if sp.get("field") == "fulltext":
        return (f"PMID {pmid} {sp.get('fulltext_source')} full text (held: outputs/k_gap/_ft, sha256 "
                f"{sp.get('fulltext_sha256')}; resolved in outputs/k_gap/exclusion_fulltext.json)")
    return f"PMID {pmid} record {sp.get('field')} (held: cache/{slug}/records.json or outputs/k_gap/member_records.json)"


_RECS = {}


def held_record(slug, pmid):
    """The record the screen read for this trial (the topic's pinned cache/<slug>/records.json, else
    outputs/k_gap/member_records.json), or None."""
    if slug not in _RECS:
        p = os.path.join(ROOT, "cache", slug, "records.json")
        rj = _j(p) if os.path.exists(p) else {}
        _RECS[slug] = {str(r.get("id")): r for r in rj.get("records", []) + rj.get("ctgov", [])}
    if "__members__" not in _RECS:
        mp = os.path.join(OUT, "member_records.json")
        _RECS["__members__"] = _j(mp) if os.path.exists(mp) else {}
    return _RECS[slug].get(str(pmid)) or _RECS["__members__"].get(str(pmid))


def span_is_verbatim(slug, pmid, span):
    """True when span['text'] occurs VERBATIM in the held record's span['field'] (a list field: in one item)."""
    if not span or not (span.get("text") or "").strip():
        return False
    if span.get("field") == "fulltext":
        # verified against the held body whose sha256 the full-text pass recorded; a clone without it fails closed
        ft = held_fulltext(pmid, span.get("fulltext_sha256"), span.get("fulltext_source"), slug)
        return bool(ft) and span["text"] in ft
    v = (held_record(slug, pmid) or {}).get(span.get("field"))
    return any(isinstance(s, str) and span["text"] in s for s in (v if isinstance(v, list) else [v]))



def demote_unstructured_secondary_single(o):
    """A lane-imported SECONDARY_SINGLE row counts only with STRUCTURED provenance -- a non-comparator meta, its figure /
    table location and a digest (secondary_single.provenance or sweep.basis) -- the rule the page's renderer applies.
    Prose-only provenance (tocilizumab CORIMUNO-TOCI-1 / EMPACTA: 'two readers agree' in a sentence) is demoted to
    UNVERIFIED with the reason recorded, so the tracker and the page count the same trials (consolidation 2026-10-04)."""
    comp = str(o.get("comparator_pmid") or "")
    for x in o.get("trials") or []:
        if x.get("route") != "SECONDARY_SINGLE" or x.get("in_our_pool"):
            continue
        cand = [(x.get("secondary_single") or {}).get("provenance"), (x.get("sweep") or {}).get("basis")]
        ok = False
        for b in cand:
            if not isinstance(b, dict):
                continue
            meta = str(b.get("meta") or b.get("meta_pmid") or "")
            if meta and meta != comp and b.get("digest") and (b.get("where") or b.get("location")):
                ok = True
        if ok:
            continue
        rt = o.setdefault("routes", {})
        rt["SECONDARY_SINGLE"] = rt.get("SECONDARY_SINGLE", 0) - 1
        rt["UNVERIFIED"] = rt.get("UNVERIFIED", 0) + 1
        if rt["SECONDARY_SINGLE"] <= 0:
            rt.pop("SECONDARY_SINGLE")
        x["provenance_refusal"] = ("SECONDARY_SINGLE without structured provenance (meta + location + digest); the lane "
                                   "file states it only as prose: " + str(x.get("basis") or "")[:200])
        x["route"], x["g1_countable"] = "UNVERIFIED", False
        if not x.get("scope_difference") and x.get("label") not in (o.get("open_gaps") or []):
            o.setdefault("open_gaps", []).append(x.get("label"))     # unmatched and not named: an OPEN gap, visibly
    if isinstance(o.get("k_matched"), int):
        o["k_matched"] = sum(1 for x in o.get("trials") or [] if is_matched(x))
    return o

def is_matched(x):
    """A comparator trial is MATCHED when it is in our pool, or when the two-source sweep verified its typed tuple
    (route SWEEP_*: two sources agreeing -- a meta row + the trial's own text, + its posted results, or two independent
    metas; never the comparator; scripts/g1_two_source_sweep.py). A lane file that does not state pool membership
    (in_our_pool null: g1/tocilizumab) counts a trial by its own verified route (g1_countable, PRIMARY / TWO_SOURCE)."""
    if x.get("in_our_pool"):
        return True
    if x.get("scope_difference"):
        return False                      # named out of scope: never matched, whatever value is held
    counted = ((x.get("g1_countable") and x.get("route") in ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE"))
               or str(x.get("route") or "").startswith("SWEEP_"))
    if counted and not screen_admits(x):
        return False                      # data held, eligibility not ours (5 Oct: being listed is never eligibility)
    return bool(counted)


def screen_admits(x):
    """ELIGIBILITY IS OUR SCREEN'S (5 Oct decision, REVIEW_REFERENCE_LIST): a comparator trial outside our pool counts
    only when OUR registered protocol's screen includes its record, or -- the screen having excluded it -- two recorded
    readers (two models, verified quotes) both judge it eligible. Being listed by the comparator is never eligibility
    evidence. A tracker object built before this gate (no screen_eligibility key: a lane's own file) is not gated here;
    the importer reports those trials as SCREEN_NOT_ASSESSED_BY_TRACKER."""
    se = x.get("screen_eligibility")
    return True if se is None else se.get("state") == "ELIGIBLE"


ROUTE_GROUP = {"PRIMARY": "PRIMARY", "SWEEP_META+TRIAL_TEXT": "PRIMARY", "SWEEP_META+AACT": "PRIMARY",
               "SWEEP_AACT_PRIMARY": "PRIMARY",
               "TWO_SOURCE": "TWO_SOURCE", "SWEEP_TWO_INDEPENDENT_METAS": "TWO_SOURCE",
               "SECONDARY_SINGLE": "SECONDARY_SINGLE", "SWEEP_SECONDARY_SINGLE": "SECONDARY_SINGLE"}


def route_group(route):
    """The headline split (Mahmood 3 Oct): PRIMARY / TWO_SOURCE / SECONDARY_SINGLE -- how much rests on another meta."""
    return ROUTE_GROUP.get(str(route), str(route))


def secondary_single(sec, metas, comp_ids, slug, mine, t):
    """SECONDARY_SINGLE (Mahmood decision 3 Oct): with NO primary source openly available after the cascade, a per-trial
    row from ONE published meta that is NOT the comparator counts, when
      - that meta reproduces its OWN printed pooled result from its rows (metas[m].usable: positive control),
      - the row passed the typed admission (sm.admit: outcome, measure, timepoint, population/subgroup) -> state
        SECONDARY_UNVERIFIED, i.e. still queued for primary verification,
      - no other non-comparator row for the trial contradicts it (MISMATCH / BLOCKED_CROSSCHECK -> flagged, refused),
      - the row is not from an uncontrolled table.
    Returns {"row", "basis", "provenance"} or {"why"} when refused, or None when there is no candidate at all."""
    ids = {str(x).strip().lower() for x in comp_ids if x}
    others = [r for r in sec if not (sm.meta_ids(r) & ids)]
    if not others:
        return None
    if any(r.state in (sm.MISMATCH, "BLOCKED_CROSSCHECK") for r in others):
        return {"why": "CONTRADICTED: " + ", ".join(f"meta {r.meta_pmid} {r.state}" for r in others
                                                    if r.state in (sm.MISMATCH, "BLOCKED_CROSSCHECK"))}
    cand = [r for r in others if r.state == sm.UNVERIFIED and (metas.get(r.meta_pmid) or {}).get("usable")
            and (metas.get(r.meta_pmid) or {}).get("positive_control", {}).get("reproduced")
            and r.provenance != "TYPED_TABLE_UNCONTROLLED"]
    if not cand:
        return {"why": "NO_ADMITTED_ROW_FROM_A_SELF_REPRODUCING_META"}
    held = primary_open(slug, mine, t)
    if held:
        return {"why": f"PRIMARY_OPENLY_AVAILABLE ({held}): extract the primary, not a meta"}
    r = cand[0]
    m = metas.get(r.meta_pmid) or {}
    where = (f"table {m.get('table')}" if m.get("provenance") == "TYPED_TABLE" else
             f"figure {m.get('figure')}{(' panel ' + str(m['panel'])) if m.get('panel') else ''} (recorded read {m.get('record_id')})")
    return {"row": r, "provenance": {"meta_pmid": r.meta_pmid, "where": where, "row_label": r.trial_label,
                                     "digest": r.source_digest, "control": m.get("positive_control"),
                                     "control_basis": m.get("control_basis") or "TYPED_TABLE"},
            "basis": (f"SECONDARY_SINGLE: meta {r.meta_pmid} {where}, row '{r.trial_label}' (digest {str(r.source_digest)[:12]}); "
                      f"the meta reproduces its own pooled result; queued for primary verification")}


def primary_open(slug, mine, t):
    """The OPEN primary sources held for one trial after the cascade: its open full text and/or bindable posted results."""
    import secondary_meta_build as smb
    out = []
    pmid = str((mine or {}).get("pmid") or "") or next(iter(t.get("pmids") or []), "")
    if pmid:
        for kind, ref, _ in smb.primary_sources(slug, pmid, (t.get("ncts") or [None])[0]):
            if kind == "text" and "abstract" not in ref:
                out.append("OPEN_FULL_TEXT")
    if t.get("ncts"):
        rb = registry_binding(t["ncts"][0], "", [])
        if rb.get("state") == "BINDABLE":
            out.append("AACT_BINDABLE")
    return sorted(set(out))


SWEEP_DIR = os.path.join(OUT, "sweep")


def comparator_rows_of(trials, measure):
    """The comparator's own per-trial rows as the tracker holds them (x['comparator_row']), as SecondaryRows."""
    out = []
    for x in trials:
        cr = x.get("comparator_row") or {}
        if not cr:
            continue
        out.append(sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                                   provenance="COMPARATOR_ROW", trial_label=x["label"],
                                   measure=(cr.get("measure") or measure or ""), outcome_definition="",
                                   **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")}))
    return out


def g1r_from_trials(o):
    """G1-R when the comparator's rows come from the forest-reader lane or a lane file (no per-meta control in our
    secondary tier): ALL the comparator rows the tracker holds, pooled by our engine, against the comparator's printed
    pooled result for the outcome (o['comparator']). Reproduced only if every row is usable and a standard estimator
    (FE / DL / PM, +/- HK) lands within the printed rounding."""
    comp = o.get("comparator") or {}
    if comp.get("estimate") is None or comp.get("ci_low") is None:
        return {"state": "NO_PRINTED_POOL", "rows": 0}
    crow = comparator_rows_of(o.get("trials") or [], comp.get("scale"))
    if len(crow) < 2:
        return {"state": "NO_PER_TRIAL_ROWS", "rows": len(crow)}
    printed = {"effect": str(comp["estimate"]), "lower": str(comp["ci_low"]), "upper": str(comp["ci_high"])}
    pc = sm.positive_control(crow, printed, (comp.get("scale") or crow[0].measure or ""))
    return {"state": "REPRODUCED" if pc.get("reproduced") else "NOT_REPRODUCED", "rows": len(crow),
            "methods": pc.get("methods"), "why": pc.get("why"), "where": "comparator rows held by the tracker",
            "control_basis": "COMPARATOR_PRINTED_POOL (served review comparator.reported)"}


def g1r_reproduction(comp_meta, comp, rows):
    """G1-R (Mahmood 3 Oct), DISTINCT FROM G1: taking the comparator's OWN per-trial rows for this outcome, does our engine
    reproduce its printed pooled result? (positive control: harness.secondary_meta.positive_control.) It says nothing
    about whether WE match the comparator -- a row whose only source is the comparator never counts toward G1."""
    crow = [r for r in rows if r.meta_pmid == comp]
    if not crow or not comp_meta:
        return {"state": "NO_PER_TRIAL_ROWS", "rows": 0}
    pc = comp_meta.get("positive_control") or {}
    where = (f"table {comp_meta.get('table')}" if comp_meta.get("provenance") == "TYPED_TABLE" else
             f"figure {comp_meta.get('figure')} (recorded read {comp_meta.get('record_id')})")
    return {"state": "REPRODUCED" if pc.get("reproduced") else "NOT_REPRODUCED", "rows": len(crow),
            "methods": pc.get("methods"), "why": pc.get("why"), "where": where,
            "control_basis": comp_meta.get("control_basis") or "TYPED_TABLE"}


def pick_comparator_row(sec, comp, label, row_owner, used_rows, label_row):
    """The comparator's OWN row for one comparator trial: ONE row joins ONE trial. The family route (our identity: a
    shared NCT) offers the family's comparator row; it is taken only when the comparator's own labels do not assign that
    row to ANOTHER of its trials and no trial took it already (ticagrelor: PLATO's row 'Wallentin 2009' was handed to
    PLATO and to its substudy Cannon 2010, whose own row then never joined). Else the trial's own label row, unused."""
    for r in sec:
        if r.meta_pmid == comp and row_owner.get(id(r), label) == label and id(r) not in used_rows:
            return r
    if label_row is not None and id(label_row) not in used_rows:
        return label_row
    return None


def ref_author_year(label, refs):
    """(surname, year) of a reference-number label ('10 [29]') from the COMPARATOR'S OWN reference list, when exactly
    one reference carries that number and states both; used only to join the comparator's rows to its trial list
    (ticagrelor: row 'Liu 2014' never joined '10 [29]'), never as an identity of ours."""
    from kgap import k_gap as _kg
    hit = _kg.refs_by_number(label, refs or {})
    if len(hit) != 1 or not hit[0].get("first_author") or not hit[0].get("year"):
        return None
    return (str(hit[0]["first_author"]).split()[0].lower(), str(hit[0]["year"]))


_COMP_REFS = {}


def comparator_refs(comp):
    """The comparator's parsed reference list from its held JATS (cache/comparators/<pmid>/<DATE>_kgap_jats.xml), {}
    when none is held."""
    if comp not in _COMP_REFS:
        import glob as _g
        from kgap import k_gap as _kg
        fs = sorted(_g.glob(os.path.join(ROOT, "cache", "comparators", str(comp), "*_kgap_jats.xml")))
        refs = {}
        if fs:
            try:
                with open(fs[-1], "rb") as fh:
                    refs = _kg.parse_jats(fh.read()).get("refs") or {}
            except Exception:  # noqa: BLE001 - an unparseable copy joins nothing
                refs = {}
        _COMP_REFS[comp] = refs
    return _COMP_REFS[comp]


def lane_comp_meta(comparator_rows_source):
    """The comparator's per-trial analysis as the forest-reader lane ACCEPTED it (dual-model read, rows reproduce the
    printed pool) in the shape outcome_set_differences / g1r read; {} when the lane accepted nothing. Without it, a topic
    whose rows come from the lane had NO comparator entry and its outcome-set rule never ran (metformin, 4 Oct)."""
    u = next((u for u in comparator_rows_source or [] if (u.get("acceptance") or {}).get("state") == "ACCEPTED"), None)
    if not u:
        return {}
    acc = u.get("acceptance") or {}
    return {"usable": True, "provenance": "FOREST_READER_DUAL", "figure": u.get("figure"), "panel": None,
            "positive_control": {"reproduced": True, "methods": acc.get("methods_reproducing")},
            "record_id": f"g1/forest-reader {str(u.get('commit'))[:9]}, figure sha256 {str(u.get('sha256'))[:12]}",
            "control_basis": f"FOREST_READER_ACCEPTANCE ({acc.get('pooled_anchor')})", "pooled": u.get("pooled_agreed")}


def pools_agree(pooled, compared):
    """The analysis's printed pool IS the compared comparator result (point and both bounds, 2-decimal printing)."""
    try:
        got = [sm._num(pooled[k]) for k in ("effect", "lower", "upper")]
        want = [float(compared[k]) for k in ("estimate", "ci_low", "ci_high")]
    except (KeyError, TypeError, ValueError):
        return None
    if None in got:
        return None
    return all(abs(a - b) <= 0.0151 for a, b in zip(got, want))


def outcome_set_differences(trials, comp_meta, comp, rows, compared=None, accounted_other=0):
    """NOT_IN_COMPARATOR_OUTCOME_ANALYSIS: G1 matches the comparator's RESULT for this outcome. When the comparator's own
    per-trial analysis of the outcome is COMPLETE and CONTROLLED -- a typed table or a gated figure read for THIS
    outcome, its rows reproducing its printed pooled result (positive control), and EVERY one of its rows joined to a
    comparator trial -- a comparator trial with NO row in it contributed nothing to that result: it is named, with the
    comparator's row list and control as the span, never silently dropped (finerenone 3 Oct: the kidney composite pool
    is FIDELIO + FIGARO; ARTS-DN (Bakris 2015, Katayama 2017) report UACR and have no row). Refused (nothing named)
    when the control did not reproduce, the read is not usable, or any comparator row is unjoined."""
    pc = comp_meta.get("positive_control") or {}
    if not (comp_meta.get("usable") and pc.get("reproduced")):
        return []
    # the analysis must BE the compared result: a figure pooling another analysis (metformin: 1.65 vs the compared
    # 2.64; tocilizumab: all IL-6 agents 0.86 vs tocilizumab 0.83) says nothing about which trials the compared one used
    if compared and pools_agree(comp_meta.get("pooled") or {}, compared) is not True:
        return []
    crow = [r for r in rows if r.meta_pmid == comp]
    joined = [x for x in trials if x.get("comparator_row")]
    # a row joined to one of the comparator's OTHER-AGENT trials (never in our list) is accounted for, not unjoined
    if not crow or len(joined) + accounted_other != len(crow):
        return []
    where = (f"table {comp_meta.get('table')}" if comp_meta.get("provenance") == "TYPED_TABLE" else
             f"figure {comp_meta.get('figure')}{(' panel ' + comp_meta['panel']) if comp_meta.get('panel') else ''} "
             f"(recorded read {comp_meta.get('record_id')})")
    span = (f"comparator PMID {comp} {where}: rows {[r.trial_label for r in crow]}; positive control reproduced "
            f"({pc.get('methods')}) against its printed pooled result ({comp_meta.get('control_basis') or 'TYPED_TABLE'})")
    named = []
    # a trial whose REPORT (family) is one a joined trial carries IS in the analysis, listed twice by the comparator
    # (balanced-crystalloids: SMART as 'Semler (SMART trial)' and 'Semler [15]', both PMID 29485925): never named absent
    in_analysis = {x.get("family"): x["label"] for x in trials if x.get("comparator_row") and x.get("family")}
    for x in trials:
        if x.get("in_our_pool") or x.get("scope_difference") or x.get("comparator_row"):
            continue
        if x.get("family") and x["family"] in in_analysis:
            x["same_report_as"] = in_analysis[x["family"]]
            continue
        x["scope_difference"] = {"kind": "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS", "rule_id": "G1-OUTCOME-SET",
                                 "protocol_rule": "G1 matches the comparator's result for this outcome",
                                 "span": {"field": "comparator outcome analysis", "text": span},
                                 "span_source": f"comparator PMID {comp} {where}", "pmid": None}
        x["blocker"] = None
        named.append(x["label"])
    return named


def sweep_results(slug):
    p = os.path.join(SWEEP_DIR, f"{slug}.json")
    return {r["label"]: r for r in (_j(p).get("trials") or [])} if os.path.exists(p) else {}


def sweep_merge(slug, trials, routes=None, pairs=None):
    """Mark every comparator trial the sweep VERIFIED (verdict SWEEP_*) as matched, with its route, value, basis and
    its agreement with the comparator's own row; add it to the same-trials pairs. Returns the labels merged."""
    sw = sweep_results(slug)
    got = []
    for x in trials:
        r = sw.get(x["label"])
        if x.get("in_our_pool") or x.get("scope_difference") or not r or not str(r.get("verdict")).startswith("SWEEP_"):
            continue
        if is_matched(x):
            continue        # never replace a trial already matched (a lane's PRIMARY / TWO_SOURCE row: in_our_pool null)
        v = r.get("value") or {}
        prim = primary_counts(x)
        if prim and v.get("events_t") is not None and tuple(prim) != (v["events_t"], v["n_t"], v["events_c"], v["n_c"]):
            # the trial's OWN primary states other counts: the meta row is flagged, never admitted (RECOVERY, 3 Oct: the
            # meta prints 596/2022 vs 694/2094; the trial's report 621/2022 vs 729/2094)
            x["secondary_single_flag"] = {"state": "CONTRADICTED_BY_PRIMARY", "meta_counts": [v["events_t"], v["n_t"],
                                          v["events_c"], v["n_c"]], "primary_counts": list(prim),
                                          "meta": (r.get("basis") or {}).get("meta")}
            continue
        if routes is not None:
            routes[x["route"]] -= 1
            routes[r["verdict"]] += 1
        x.update(route=r["verdict"], matched_by="SWEEP", basis=f"two-source sweep: {r['verdict']}",
                 sweep={k: r.get(k) for k in ("value", "basis", "agreement_with_comparator_row")},
                 g1_countable=True, blocker=None, our_value=r.get("value"),
                 agreement_with_comparator_row=r.get("agreement_with_comparator_row") or "NOT_COMPARABLE:NO_COMPARATOR_ROW")
        cr = x.get("comparator_row")
        v = r.get("value") or {}
        if pairs is not None and cr and v.get("measure") not in (None, "COUNTS"):
            theirs = sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                                     provenance="COMPARATOR_ROW", trial_label=x["label"], measure=cr.get("measure") or "",
                                     outcome_definition="", **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t",
                                                                                       "n_t", "events_c", "n_c")})
            pairs.append((as_row(v, x["label"], theirs.measure), theirs))
        got.append(x["label"])
    if routes is not None:
        for k in [k for k, n in routes.items() if n <= 0]:
            del routes[k]
    return got


def acquired_rows(slug):
    """ADMITTED rows of scripts/g1_trial_acquire.py for a topic (registry/g1_acquired/<slug>.json), by trial label."""
    p = os.path.join(ROOT, "registry", "g1_acquired", f"{slug}.json")
    if not os.path.exists(p):
        return {}
    return {r["label"]: r for r in _j(p).get("rows") or [] if r.get("verdict") == "ADMITTED" and r.get("admitted")}


def acquired_merge(slug, trials, routes=None, pairs=None, comp=None):
    """A comparator trial whose ONE PRIMARY source (its own open text, or its posted AACT results) gave a typed tuple
    through scripts/g1_trial_acquire.py's gates is PRIMARY-verified (2 Oct decision, restated 3 Oct; the rule of
    single_primary_source): matched, countable, compared on that tuple. A SECONDARY_SINGLE trial is PROMOTED -- its meta
    pair in the same-trials comparison is replaced by the primary tuple. Never a pooled, named or already-PRIMARY trial.
    Returns the labels merged."""
    acq = acquired_rows(slug)
    got = []
    for x in trials:
        a = acq.get(x["label"])
        if not a or x.get("in_our_pool") or x.get("scope_difference"):
            continue
        promote = x.get("route") == "SECONDARY_SINGLE"
        if is_matched(x) and not promote:
            continue
        ad = a["admitted"]
        v = ad.get("value") or {}
        cr = x.get("comparator_row")
        theirs = None
        if cr:
            theirs = sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                                     provenance="COMPARATOR_ROW", trial_label=x["label"], measure=cr.get("measure") or "",
                                     outcome_definition="", **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t",
                                                                                       "n_t", "events_c", "n_c")})
        if pairs is not None and promote and cr:
            same = [i for i, (_o, t) in enumerate(pairs)
                    if t.meta_pmid == str(comp) and all(str(getattr(t, k)) == str(cr.get(k)) for k in
                                                        ("effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c"))]
            for i in reversed(same):
                pairs.pop(i)
        if routes is not None:
            routes[x["route"]] -= 1
            routes["PRIMARY"] += 1
        x.update(route="PRIMARY", g1_countable=True, blocker=None, our_value=v, matched_by="ACQUIRED_PRIMARY",
                 basis=f"single PRIMARY source (2 Oct decision): {ad['kind']} {ad['source']}; model-read (record "
                       f"{a.get('record_id')}), gate-verified (scripts/g1_trial_acquire.py)",
                 acquired={"kind": ad["kind"], "source": ad["source"], "span": ad.get("span"), "quote": ad.get("quote"),
                           "record_id": a.get("record_id"), "promoted_from": "SECONDARY_SINGLE" if promote else None},
                 agreement_with_comparator_row=agreement(v, theirs) if theirs is not None else
                 "NOT_COMPARABLE:NO_COMPARATOR_ROW")
        chk = ad.get("comparator_counts_check")
        if chk and str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE"):
            # the comparator's counts are the trial's posted EVENT counts (AFFIRM-AHF 217 vs 294, units Events) pooled over
            # participant denominators: the disagreement falls on the comparator's side
            x["disagreement_side"] = (f"SECONDARY_WRONG (the comparator's counts {chk['comparator_counts']} are the posted "
                                      f"'{chk['title']}' measurements in {chk['units']}, not participants; "
                                      f"{chk['nct']} outcome {chk['outcome_id']})")
        if pairs is not None and theirs is not None:
            pairs.append((as_row(v, x["label"], theirs.measure), theirs))
        got.append(x["label"])
    if routes is not None:
        for k in [k for k, n in routes.items() if n <= 0]:
            del routes[k]
    return got


_COUNT_KEYS = ("deaths_t", "n_t", "deaths_c", "n_c")


def single_primary_source(x):
    """2 Oct decision (restated 3 Oct): a typed tuple bound to ONE PRIMARY source (the trial's own open text, or its
    posted CT.gov results) is PRIMARY-verified; the two-source rule is for SECONDARY sources (metas) only. A lane row
    held at g1_state ONE_SOURCE with a single primary source qualifies only through the SAME typed requirements:
      TEXT  every count is printed verbatim (as a whole number) in the quoted span of the trial's own report
      AACT  counts are posted participant counts, never derived from a posted percentage ('84% of 49 -> 8 deaths' is a
            reconstruction: refused, as the registry rung refuses EXAMINE's 11.3%) and from ONE time frame
    Returns (True, basis) or (False, why)."""
    rd = x.get("readings") or []
    if x.get("g1_state") != "ONE_SOURCE" or len(rd) != 1:
        return False, "NOT_A_SINGLE_SOURCE_ROW"
    r = rd[0]
    vals = r.get("values") or {}
    if not all(isinstance(vals.get(k), int) for k in _COUNT_KEYS):
        return False, "COUNTS_NOT_TYPED"
    srcs = r.get("sources") or []
    kinds = {str(s.get("source") or "").split()[0] for s in srcs}
    if kinds == {"TEXT"}:
        import re as _re
        for s in srcs:
            span = s.get("span") or ""
            if not all(_re.search(rf"(?<![\d.,]){v:,}(?![\d])|(?<![\d.,]){v}(?![\d])", span) for v in (vals[k] for k in _COUNT_KEYS)):
                return False, "COUNTS_NOT_IN_SPAN"
        return True, f"single PRIMARY source: trial's own text, counts verbatim in span ({srcs[0].get('source')})"
    if kinds == {"AACT"}:
        for s in srcs:
            if "%" in str(s.get("derivation") or ""):
                return False, "AACT_COUNTS_DERIVED_FROM_PERCENTAGE"
            if "," in str(s.get("time_frame") or "") or " and " in str(s.get("time_frame") or ""):
                return False, "AACT_MULTIPLE_TIME_FRAMES"
        return True, "single PRIMARY source: posted CT.gov participant counts (AACT)"
    return False, f"SOURCE_KINDS_{sorted(kinds)}"


def apply_single_primary(o):
    """Reclassify a lane's ONE_SOURCE rows whose single source is PRIMARY and typed (single_primary_source): route
    PRIMARY, countable. Every row examined records the decision (primary_single_source)."""
    flipped = []
    for x in o.get("trials") or []:
        if x.get("route") != "UNVERIFIED" or x.get("g1_state") != "ONE_SOURCE":
            continue
        ok, why = single_primary_source(x)
        x["primary_single_source"] = {"admitted": ok, "why": why}
        if ok:
            x.update(route="PRIMARY", g1_countable=True, basis=why, reclassified_by="acq/k-gap single_primary_source")
            flipped.append(x["label"])
    if flipped:
        tr = o["trials"]
        o["routes"] = dict(Counter(x["route"] for x in tr))
        o["k_matched"] = sum(1 for x in tr if is_matched(x))
        o["k_matched_of_comparator_N"] = f"{o['k_matched']} of {len(tr)}"
        o["open_gaps"] = [g for g in o.get("open_gaps") or [] if g not in flipped]
        o["single_primary_reclassified"] = flipped
    return flipped


CONFIRM_BINDINGS = os.path.join(OUT, "g1_confirm", "bindings.json")
# A primary binding confirms the comparator's NUMBER; it must never override a typed reason the number is not this
# topic's result (CONFREV, 3 Oct: ELIXA's 4-point composite, Siebert's non-placebo contrast, Wenus' per-protocol RR 0.21
# were all bound while the tracker already refused them).
CONFIRM_BLOCKING_ABSENT = {"ENGINE_CANNOT_CONSUME", "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH", "ENDPOINT_UNBOUND",
                           "RESULT_INCOMPATIBLE"}
import re as _cre  # noqa: E402
CONFIRM_BLOCKING_REFUSAL = _cre.compile(r"per[- ]?protocol|completers?\b|completed the study|population mismatch|"
                                        r"subgroup|different composite|estimand|cluster|cross-?over|post[- ]?hoc", _cre.I)


def confirm_blocked(x):
    """Why a comparator trial may NOT be confirmed by a primary binding, or None: out of the topic's scope (a named
    scope / estimand difference), or our own typed refusal says the comparator's value is not the trial's result for
    this topic (design, estimand, population)."""
    if x.get("scope_difference"):
        return f"NOT_ELIGIBLE:{(x['scope_difference'] or {}).get('kind')}"
    if x.get("absent_code") in CONFIRM_BLOCKING_ABSENT:
        return f"TYPED_REFUSAL:{x['absent_code']}"
    m = CONFIRM_BLOCKING_REFUSAL.search(x.get("our_refusal") or "")
    if m:
        return f"TYPED_REFUSAL_NAMES:{m.group(0).lower()}"
    return None


def apply_confirm_bindings(o, path=CONFIRM_BINDINGS):
    """G1 confirm-unverified (scripts/g1_confirm_bind.py, Mahmood 3 Oct): an UNVERIFIED comparator trial whose typed tuple
    is printed by its OWN primary source -- the trial's open report or its posted CT.gov results -- is PRIMARY (2 Oct
    decision: one primary source suffices). Re-checked here, offline, from the committed binding:
      COUNTS     through single_primary_source, unchanged (every count verbatim in the quoted span)
      EFFECT_CI  the span prints the effect and both CI bounds verbatim
    The comparator's row was the SEARCH KEY: agreement with it is true by construction and is recorded
    NOT_INDEPENDENT, never AGREE (it must not inflate per-trial agreement). Rows not UNVERIFIED are never touched."""
    if not os.path.exists(path):
        return []
    by = {b["label"]: b for b in (_j(path).get("bindings") or []) if b.get("slug") == o.get("slug")}
    flipped = []
    for x in o.get("trials") or []:
        b = by.get(x["label"])
        # an OWN-TUPLE binding (the trial's own printed tuple, not the comparator's) may also bind a NO_ROW trial: it
        # needs no comparator row (g1/binding lane, scripts/g1_binding_bind.py)
        if not b or not (x.get("route") == "UNVERIFIED" or (b.get("own_tuple") and x.get("route") == "NO_ROW")):
            continue
        v, span = b.get("values") or {}, b.get("span") or ""
        src = f"{'TEXT' if b.get('source_kind') == 'TEXT' else 'AACT'} {b.get('source')}"
        blocked = confirm_blocked(x)
        arms = None
        if not blocked and b.get("tuple_kind") == "COUNTS" and b.get("source_kind") == "TEXT":
            # arm ownership RE-CHECKED from the committed span, never taken from the binder's own verdict
            import g1_confirm_bind as _cb
            row = _cb.key_row(o.get("slug"), {"label": x["label"], "comparator_row": {
                "events_t": v.get("events_t"), "n_t": v.get("n_t"), "events_c": v.get("events_c"), "n_c": v.get("n_c")}})
            arms = (_cb.arm_check(row, span, *_cb.arm_terms(o.get("slug"))) if not b.get("span_parts")
                    else b.get("arm_check"))
            if arms in ("SWAPPED", "CONFLICT"):
                blocked = "ARM_COUNTS_SWAPPED"
        if blocked:
            x["confirm_binding"] = {"admitted": False, "why": blocked, "source": b.get("source"),
                                    "pmid": b.get("pmid"), "tuple_kind": b.get("tuple_kind")}
            continue
        if b.get("tuple_kind") == "COUNTS":
            probe = dict(x, g1_state="ONE_SOURCE", readings=[{
                "values": {"deaths_t": v.get("events_t"), "n_t": v.get("n_t"), "deaths_c": v.get("events_c"),
                           "n_c": v.get("n_c")},
                "sources": [{"source": src, "span": span}]}])
            ok, why = single_primary_source(probe)
        else:
            flat = span.replace(",", "")
            ok = all(str(v.get(k) or "") and str(v.get(k)) in flat for k in ("effect", "lower", "upper"))
            why = ("single PRIMARY source: effect + CI verbatim in the trial's own span" if ok
                   else "EFFECT_CI_NOT_IN_SPAN")
        x["confirm_binding"] = {"admitted": ok, "why": why, "source": b.get("source"), "pmid": b.get("pmid"),
                                "source_sha256": b.get("source_sha256"), "tuple_kind": b.get("tuple_kind"),
                                "search_key": b.get("search_key")}
        if not ok:
            continue
        if b.get("own_tuple"):
            # the trial's OWN printed counts for the topic outcome (Mahmood 3 Oct: matched = any verified typed tuple for
            # the comparator's trial): NOT searched by the comparator's numbers, so agreement is COMPUTED, never assumed
            cr = x.get("comparator_row") or {}
            ours = {"measure": (cr.get("measure") or "").upper(), "effect": None, "lower": None, "upper": None,
                    **{k: v.get(k) for k in ("events_t", "n_t", "events_c", "n_c")}}
            theirs = sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                                     provenance="COMPARATOR_ROW", trial_label=x["label"],
                                     measure=(cr.get("measure") or "").upper(), outcome_definition="",
                                     **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t", "n_t",
                                                               "events_c", "n_c")}) if cr else None
            x.update(route="PRIMARY", g1_countable=True, our_value=ours,
                     basis=f"{why} ({b.get('source')}); the trial's own tuple (reading lane proposal, gated)",
                     reclassified_by="g1/confirm-unverified primary binding (own tuple)",
                     agreement_with_comparator_row=agreement(ours, theirs) if theirs else "NOT_COMPARABLE:NO_COMPARATOR_ROW",
                     blocker=None)
        else:
            x.update(route="PRIMARY", g1_countable=True, basis=f"{why} ({b.get('source')}); search key: comparator row",
                     reclassified_by="g1/confirm-unverified primary binding",
                     agreement_with_comparator_row="NOT_INDEPENDENT:SEARCH_KEYED_BY_COMPARATOR_ROW",
                     blocker=None)
        flipped.append(x["label"])
    if flipped:
        tr = o["trials"]
        o["routes"] = dict(Counter(x["route"] for x in tr))
        o["k_matched"] = sum(1 for x in tr if is_matched(x))
        o["k_matched_of_comparator_N"] = f"{o['k_matched']} of {len(tr)}"
        o["open_gaps"] = [g for g in o.get("open_gaps") or [] if g not in flipped]
        o["per_trial_agreement"] = dict(Counter(x.get("agreement_with_comparator_row") for x in tr if is_matched(x)))
        bl = Counter(x["blocker"] for x in tr if x.get("blocker") and not is_matched(x))
        o["blockers"], o["top_blocker"] = dict(bl), (bl.most_common(1)[0][0] if bl else None)
        o["confirm_bindings_flipped"] = flipped
    return flipped


def apply_secondary_bindings(o, path):
    """SECONDARY_SINGLE from a meta's open SUPPLEMENTARY table (scripts/g1_binding_secondary.py, g1/binding lane):
    Mahmood 3 Oct conditions, re-checked here offline from the committed file -- the meta is not the comparator (PMID or
    DOI), its printed pooled results were reproduced from its own rows (positive_control.reproduced), the row was
    admitted by the typed rules S3, and the trial holds no other route (NO_ROW / UNVERIFIED only). Agreement with the
    comparator's row is COMPUTED (the comparator's numbers were never the search key)."""
    if not os.path.exists(path):
        return []
    s = _j(path)
    comp = {str(o.get("comparator_pmid")), str(o.get("comparator_doi") or "").lower()} - {"", "None", "none"}
    if s.get("slug") != o.get("slug") or not (s.get("positive_control") or {}).get("reproduced") \
            or {str(s.get("meta_pmid")), str(s.get("meta_doi") or "").lower()} & comp:
        return []
    by = {b["label"]: b for b in s.get("bindings") or [] if b.get("admitted")}
    flipped = []
    for x in o.get("trials") or []:
        b = by.get(x["label"])
        if not b or x.get("route") not in ("NO_ROW", "UNVERIFIED") or x.get("scope_difference"):
            continue
        v = b.get("values") or {}
        if not all(isinstance(v.get(k), int) for k in ("events_t", "n_t", "events_c", "n_c")):
            continue
        cr = x.get("comparator_row") or {}
        ours = {"measure": (cr.get("measure") or "RR").upper(), "effect": None, "lower": None, "upper": None,
                **{k: v[k] for k in ("events_t", "n_t", "events_c", "n_c")}}
        theirs = sm.SecondaryRow(meta_pmid="COMPARATOR", meta_doi="", location={}, source_digest="",
                                 provenance="COMPARATOR_ROW", trial_label=x["label"],
                                 measure=(cr.get("measure") or "").upper(), outcome_definition="",
                                 **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t", "n_t", "events_c",
                                                           "n_c")}) if cr.get("measure") else None
        x.update(route="SECONDARY_SINGLE", g1_countable=True, our_value=ours, blocker=None,
                 basis=(f"SECONDARY_SINGLE: meta {s['meta_pmid']} supplementary table (sha256 "
                        f"{str(s.get('supplement_sha256'))[:12]}), row '{b.get('source_row_key')}'; the meta reproduces its "
                        f"own pooled result; queued for primary verification"),
                 reclassified_by="g1/binding secondary supplement (scripts/g1_binding_secondary.py)",
                 agreement_with_comparator_row=agreement(ours, theirs) if theirs else "NOT_COMPARABLE:NO_COMPARATOR_ROW")
        flipped.append(x["label"])
    if flipped:
        tr = o["trials"]
        o["routes"] = dict(Counter(x["route"] for x in tr))
        o["k_matched"] = sum(1 for x in tr if is_matched(x))
        o["k_matched_of_comparator_N"] = f"{o['k_matched']} of {len(tr)}"
        o["open_gaps"] = [g for g in o.get("open_gaps") or [] if g not in flipped]
        o["per_trial_agreement"] = dict(Counter(x.get("agreement_with_comparator_row") for x in tr if is_matched(x)))
        bl = Counter(x["blocker"] for x in tr if x.get("blocker") and not is_matched(x))
        o["blockers"], o["top_blocker"] = dict(bl), (bl.most_common(1)[0][0] if bl else None)
        o["secondary_bindings_flipped"] = flipped
    return flipped


def primary_counts(x):
    """Counts a trial's OWN primary states (a lane reading whose counts are printed by a primary -- TEXT or posted
    results -- not only by a meta), as (events_t, n_t, events_c, n_c), or None."""
    for rd in x.get("readings") or []:
        v = rd.get("values") or {}
        by_primary = [s for s in rd.get("sources") or [] if str(s.get("source") or "").split()[0] in ("TEXT",)
                      and s.get("span")]
        if by_primary and all(isinstance(v.get(k), int) for k in ("deaths_t", "n_t", "deaths_c", "n_c")):
            return (v["deaths_t"], v["n_t"], v["deaths_c"], v["n_c"])
    return None


CS_OK_STATES = (None, sm.UNVERIFIED, sm.VERIFIED, sm.TWO_SOURCE)


def orientation(o):
    """Is the comparator's arm orientation OURS? Established only by the trials both sides hold: >= 1 independently
    confirmed trial whose value AGREES with its comparator row and none that DISAGREES. Melatonin (3 Oct): the
    comparator's rows are +8.9 ... +38.7 minutes where ours is -17.4 -- with no shared trial, its orientation is unknown,
    and pooling the two would mix 'placebo minus melatonin' with 'melatonin minus placebo'."""
    shared = [x for x in o.get("trials") or [] if is_matched(x) and x.get("comparator_row")]
    agree = [x for x in shared if str(x.get("agreement_with_comparator_row") or "").startswith("AGREE")]
    # a DISAGREEMENT disputes orientation only when the comparator's row MIRRORS ours (reciprocal ratio, negated
    # difference, swapped arm counts); a different number in the same direction is a discrepancy finding, not a flip
    mirrored = [x for x in shared if str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE")
                and _mirrors(x.get("our_value") or {}, x.get("comparator_row") or {})]
    if mirrored:
        return "DISPUTED", f"{len(mirrored)} shared trial(s) mirror our orientation"
    if agree:
        return "ESTABLISHED", f"{len(agree)} shared trial(s) AGREE"
    # measures differ (our HR vs their RR / OR): orientation is DIRECTION, not value -- a shared pair of ratio
    # estimates both clearly off the null (beyond +/-10%) on the SAME side establishes it (omega-3: REDUCE-IT HR 0.74
    # vs RR 0.78; ticagrelor HR 0.84 vs OR 0.83); a near-null pair says nothing
    same_side = []
    for x in shared:
        a, b = sm._num((x.get("our_value") or {}).get("effect")), sm._num((x.get("comparator_row") or {}).get("effect"))
        ma, mb = ((x.get("our_value") or {}).get("measure") or "").upper(), ((x.get("comparator_row") or {}).get("measure") or "").upper()
        if a and b and a > 0 and b > 0 and ma in sm.RATIO and mb in sm.RATIO:
            la, lb = math.log(a), math.log(b)
            if min(abs(la), abs(lb)) >= math.log(1.1) and la * lb > 0:
                same_side.append(x["label"])
    if same_side:
        return "ESTABLISHED", f"{len(same_side)} shared trial(s) on the same side of the null ({', '.join(same_side[:3])})"
    return "UNKNOWN", "no shared trial agrees or shows the direction"


def _mirrors(ours, theirs):
    """theirs IS ours with the arms swapped: counts exactly swapped, or every printed number (point and both bounds)
    the reciprocal (ratio) / negation (difference) of ours within the printed rounding (3 half-units, as the positive
    control). Merely landing on the other side of the null is NOT a mirror: Pozzoni (probiotics, 4 Oct) -- 1.14 vs 0.75,
    whose reciprocal is 1.33 -- is a discrepancy, and calling it a mirror DISPUTED an orientation 13 trials establish."""
    ot = tuple(ours.get(k) for k in ("events_t", "n_t", "events_c", "n_c"))
    tt = tuple(theirs.get(k) for k in ("events_t", "n_t", "events_c", "n_c"))
    if None not in ot and None not in tt:
        return (tt[2], tt[3], tt[0], tt[1]) == ot and tt != ot
    pairs = [("effect", "effect"), ("lower", "upper"), ("upper", "lower")]
    ratio = (ours.get("measure") or "").upper() in sm.RATIO
    seen = 0
    for ko, kt in pairs:
        a, b = sm._num(ours.get(ko)), sm._num(theirs.get(kt))
        if a is None or b is None:
            if ko == "effect":
                return False
            continue
        ha, hb = sm._half(str(ours.get(ko))) * 3, sm._half(str(theirs.get(kt))) * 3
        if ratio:
            if a <= 0 or b <= 0:
                return False
            if abs(math.log(a) + math.log(b)) > ha / a + hb / b + 1e-9:
                return False
        elif abs(a + b) > ha + hb + 1e-9:
            return False
        seen += 1
    a, b = sm._num(ours.get("effect")), sm._num(theirs.get("effect"))
    return seen >= 1 and ((math.log(a) * math.log(b) < 0) if ratio else (a * b < 0))


def comparator_sourced(x, g1r_state, orient="ESTABLISHED"):
    """COMPARATOR_SOURCED (Mahmood decision 3 Oct) -- COVERAGE ONLY, never independent confirmation: a comparator trial
    not independently confirmed (and not named out of scope) is filled from the comparator meta's OWN per-trial row when
      - the comparator self-reproduces its pooled result from its rows (G1-R REPRODUCED),
      - its arm orientation is ours (orientation ESTABLISHED by a shared trial; the typed tuple's 'arms'),
      - the row passed the typed admission (state not REFUSED / MISMATCH / BLOCKED_CROSSCHECK) and, read by two
        models, the readers agree (comparator_row_readings not READERS_DIFFER),
      - the row carries its provenance: the table/figure location AND a digest or read record (shown on the page).
    Returns ({"value", "provenance"}, None) or (None, why)."""
    cr = x.get("comparator_row")
    if not cr:
        return None, "NO_COMPARATOR_ROW"
    if g1r_state != "REPRODUCED":
        return None, f"COMPARATOR_DOES_NOT_SELF_REPRODUCE ({g1r_state})"
    if orient != "ESTABLISHED":
        return None, f"COMPARATOR_ARM_ORIENTATION_{orient}"
    # a row refused ONLY because OUR identity of the trial is unresolved (FAMILY_NOT_RESOLVED) passed every typed check;
    # it is the comparator's own row for the comparator's own trial, joined by the comparator's labels (omega3, 4 Oct)
    bookkeeping_only = (x.get("comparator_row_state") == "REFUSED"
                        and set(x.get("comparator_row_reasons") or []) == {"FAMILY_NOT_RESOLVED"})
    if x.get("comparator_row_state") not in CS_OK_STATES and not bookkeeping_only:
        return None, f"COMPARATOR_ROW_{x.get('comparator_row_state')}"
    if (x.get("comparator_row_readings") or {}).get("state") == "READERS_DIFFER":
        return None, "COMPARATOR_ROW_READERS_DIFFER"
    pv = x.get("comparator_row_provenance") or {}
    if not ((pv.get("location") or {}).get("id") and (pv.get("digest") or pv.get("read"))):
        return None, "COMPARATOR_ROW_PROVENANCE_MISSING (no table/figure location + digest)"
    return {"value": {k: cr.get(k) for k in ("measure", "effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")},
            "provenance": x.get("comparator_row_provenance") or {}}, None


def count_stated(text, a, n):
    """The span where the text STATES a events of n ('13/98', '4 (3.9%) of 103', '9 of 103'), else None."""
    m = re.search(rf"(?<![\d.]){a}\s*/\s*{n}(?![\d.])|(?<![\d.]){a}\s*\(\s*[\d.]+\s*%\s*\)\s*of\s*{n}(?![\d.])|"
                  rf"(?<![\d.]){a}\s+of\s+(?:the\s+)?{n}(?![\d.])", text or "")
    return m.group(0) if m else None


def disagreement_side(ours, theirs, text):
    """Which side of an ours-vs-comparator DISAGREE the trial's OWN held text supports, or None:
      COMPARATOR_ARMS_SWAPPED            the comparator's numerators appear stated with their denominators exchanged
                                         (Pozzoni: report '16/106' S. boulardii, '13/98' placebo; comparator 13/106 vs 16/98)
      COMPARATOR_ROW_NOT_IN_TRIAL_REPORT  our counts are stated in the report, the comparator's are not
                                         (Song: report '4 (3.9%) of 103' and '8 (7.2%) of 111'; comparator 9/103 vs 16/111)"""
    if not text or None in (theirs.get("events_t"), theirs.get("n_t"), theirs.get("events_c"), theirs.get("n_c")):
        return None
    a, n1, b, n2 = (theirs[k] for k in ("events_t", "n_t", "events_c", "n_c"))
    direct = count_stated(text, a, n1) and count_stated(text, b, n2)
    sw = (count_stated(text, b, n1), count_stated(text, a, n2))
    if not direct and all(sw) and (a, n1) != (b, n2):
        return f"COMPARATOR_ARMS_SWAPPED (the trial's report states '{sw[0]}' and '{sw[1]}')"
    if ours and ours.get("events_t") is not None:
        s1, s2 = count_stated(text, ours["events_t"], ours["n_t"]), count_stated(text, ours["events_c"], ours["n_c"])
        if s1 and s2 and not direct:
            return f"COMPARATOR_ROW_NOT_IN_TRIAL_REPORT (the trial's report states '{s1}' and '{s2}'; the comparator's counts appear nowhere in it)"
        if s1 and s2 and direct:
            # the report states BOTH: two definitions of the outcome (Song: 'AAD-1' 4/103 vs 8/111 is the abstract's
            # primary, 'AAD-2' 9/103 vs 16/111 is what the comparator pooled) -- neither side is wrong
            d1, d2 = count_stated(text, a, n1), count_stated(text, b, n2)
            return (f"BOTH_STATED_DIFFERENT_DEFINITIONS (the trial's report states ours '{s1}' / '{s2}' and the "
                    f"comparator's '{d1}' / '{d2}')")
    return None


def side_from_trial_text(trials, slug):
    """A per-trial DISAGREE with no side yet takes the side the trial's own held record supports (title + abstract +
    held full text), so DIVERGENCES_NAMED can be met by evidence rather than left open."""
    recs = {}
    for f in (os.path.join(ROOT, "cache", slug, "records.json"), os.path.join(OUT, "member_records.json")):
        if os.path.exists(f):
            d = _j(f)
            for v in (d.values() if isinstance(d, dict) else [d]):
                for r in (v if isinstance(v, list) else [v]):
                    if isinstance(r, dict) and r.get("id"):
                        recs[str(r["id"])] = r
    for x in trials:
        if not str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE") or x.get("disagreement_side"):
            continue
        pm = str(x.get("family") or "").replace("PMID ", "")
        r = recs.get(pm) or {}
        ft = os.path.join(ROOT, "cache", slug, f"ft_{pm}.txt")
        text = " ".join([r.get("title") or "", r.get("abstract") or "",
                         open(ft, encoding="utf-8", errors="replace").read() if os.path.exists(ft) else ""])
        side = disagreement_side(x.get("our_value"), x.get("comparator_row") or {}, text)
        if side:
            x["disagreement_side"] = side


def discrepancy_findings(o):
    """Typed DISCREPANCY FINDINGS (never a silent overwrite of either side): every trial where our own value (pool /
    primary) and the comparator's row DISAGREE, every comparator row our primary verification contradicted (MISMATCH),
    and every non-comparator meta row a trial's own report contradicts (CONTRADICTED_BY_PRIMARY)."""
    out = []
    for x in o.get("trials") or []:
        ag = str(x.get("agreement_with_comparator_row") or "")
        if ag.startswith("DISAGREE"):
            out.append({"trial": x["label"], "kind": "OURS_VS_COMPARATOR_ROW", "detail": ag,
                        "ours": x.get("our_value"), "ours_source": (x.get("basis") or "")[:200],
                        "comparator_row": x.get("comparator_row"), "side": x.get("disagreement_side") or "UNRESOLVED"})
        if x.get("comparator_row_state") == sm.MISMATCH:
            out.append({"trial": x["label"], "kind": "COMPARATOR_ROW_CONTRADICTED_BY_PRIMARY",
                        "comparator_row": x.get("comparator_row"), "side": x.get("disagreement_side") or "UNRESOLVED"})
        f = x.get("secondary_single_flag")
        if f:
            out.append({"trial": x["label"], "kind": "SECONDARY_META_CONTRADICTED_BY_PRIMARY", "meta": f.get("meta"),
                        "meta_counts": f.get("meta_counts"), "primary_counts": f.get("primary_counts"),
                        "side": "SECONDARY_META_WRONG (the trial's own report states the counts)"})
    return out


def apply_coverage(o):
    """The SCOREBOARD's second number. Per trial: coverage INDEPENDENT (is_matched) / COMPARATOR_SOURCED / None, with
    the refusal reason; per topic: k_covered, coverage_complete, discrepancy_findings. G1_MATCHED is untouched."""
    g1r = (o.get("g1r_reproduction") or {}).get("state")
    orient, orient_why = orientation(o)
    o["comparator_orientation"] = {"state": orient, "why": orient_why}
    for x in o.get("trials") or []:
        x.pop("comparator_sourced", None)
        x.pop("comparator_sourced_refusal", None)
        x.pop("count_refusal", None)
        if not x.get("in_our_pool") and not screen_admits(x) and not x.get("scope_difference") and (
                (x.get("g1_countable") and x.get("route") in ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE"))
                or str(x.get("route") or "").startswith("SWEEP_")):
            se = x["screen_eligibility"]
            x["count_refusal"] = f"NOT_SCREEN_ELIGIBLE:{se.get('state')}:{se.get('rule_id') or se.get('why') or ''}"
        if is_matched(x):
            x["coverage"] = "INDEPENDENT"
            continue
        if x.get("scope_difference"):
            x["coverage"] = None
            continue
        cs, why = comparator_sourced(x, g1r, orient)
        x["coverage"] = "COMPARATOR_SOURCED" if cs else None
        if cs:
            x["comparator_sourced"] = cs
        else:
            x["comparator_sourced_refusal"] = why
    tr = o.get("trials") or []
    o["k_independent"] = sum(1 for x in tr if x.get("coverage") == "INDEPENDENT")
    o["k_comparator_sourced"] = sum(1 for x in tr if x.get("coverage") == "COMPARATOR_SOURCED")
    o["k_covered"] = o["k_independent"] + o["k_comparator_sourced"]
    elig = [x for x in tr if not x.get("scope_difference")]
    o["coverage_complete"] = bool(elig) and all(x.get("coverage") for x in elig)
    o["discrepancy_findings"] = discrepancy_findings(o)
    return o


def apply_sweep(o, slug):
    """sweep_merge for an already-built tracker object (a lane's imported file): counts, gaps and blockers recomputed;
    its same-trials result is NOT recomputed here (recorded as such)."""
    got = sweep_merge(slug, o.get("trials") or [])
    if not got:
        return o
    tr = o["trials"]
    o["routes"] = dict(Counter(x["route"] for x in tr))
    o["k_matched"] = sum(1 for x in tr if is_matched(x))
    o["k_matched_of_comparator_N"] = f"{o['k_matched']} of {len(tr)}"
    o["open_gaps"] = [g for g in o.get("open_gaps") or [] if g not in got]
    bl = Counter(x["blocker"] for x in tr if x.get("blocker") and not is_matched(x))
    o["blockers"], o["top_blocker"] = dict(bl), (bl.most_common(1)[0][0] if bl else None)
    o["sweep_merged"] = {"trials": got, "same_trials_recomputed": False}
    return o


def scope_citation_violations(o):
    """Every comparator trial must be MATCHED (in our pool), an OPEN gap (eligible, counted against us), or a NAMED
    difference citing a rule ID AND a source span. Anything else silently shrinks the eligible denominator (Mahmood 3
    Oct: 'shrinking the denominator is exactly how a match metric gets gamed'). Returns the violations, [] when clean."""
    tr = o.get("trials") or []
    named = {d.get("trial"): d for d in o.get("named_differences") or []}
    gaps = set(o.get("open_gaps") or [])
    bad = []
    for x in tr:
        lab = x.get("label")
        if is_matched(x):
            if lab in named or lab in gaps:
                bad.append(f"{lab}: matched AND listed as non-eligible/open")
            continue
        d = named.get(lab)
        if d is None:
            if lab not in gaps:
                bad.append(f"{lab}: not matched, not an open gap, not named -- dropped from the denominator")
            continue
        if lab in gaps:
            bad.append(f"{lab}: both named and an open gap")
        if not (d.get("rule_id") or d.get("gate")):
            bad.append(f"{lab}: non-eligible without a cited rule ID")
        sp = d.get("span") or {}
        if not (sp.get("text") or "").strip() or not d.get("span_source"):
            bad.append(f"{lab}: non-eligible without a source span")
    for lab in named:
        if lab not in {x.get("label") for x in tr}:
            bad.append(f"{lab}: named difference for a trial not in the comparator set")
    if tr and o.get("k_matched") is not None and o["k_matched"] != sum(1 for x in tr if is_matched(x)):
        bad.append(f"k_matched {o['k_matched']} != matched trials {sum(1 for x in tr if is_matched(x))}")
    if tr and o.get("N_eligible") != len(tr) - len(named):
        bad.append(f"N_eligible {o.get('N_eligible')} != comparator N {len(tr)} - named {len(named)}")
    return bad


def cite_or_demote(o, slug):
    """A NAMED scope difference carries its rule ID and its span (from the exclusion audit, verbatim in the held record);
    one that cannot is DEMOTED to an open gap -- the trial goes back into the eligible denominator, its blocker says why.
    Used for every topic, including a lane's imported file (the lane's naming is not taken on its word)."""
    keep, demoted = [], []
    by_label = {x.get("label"): x for x in o.get("trials") or []}
    # SYMMETRY: the same rule that names a difference in this lane's topics names it in a lane's file -- a trial
    # screened out under a rule, audited TRUE_SCOPE_DIFFERENCE with a verbatim span, is named (SOLOIST-WHF, 3 Oct: the
    # lane stopped naming it; the audit, now reading allocation sentences, establishes it)
    named0 = {d.get("trial") for d in o.get("named_differences") or []}
    cfg_p = os.path.join(ROOT, "topics", slug + ".json")
    cfg = _j(cfg_p) if os.path.exists(cfg_p) else {}
    for x in o.get("trials") or []:
        f = x.get("seeded_funnel") or {}
        if is_matched(x) or x.get("label") in named0 or f.get("stage") != "SCREENED_OUT" or not f.get("rule_id"):
            continue
        sp = exclusion_audit_span(slug, f.get("pmid"))
        if sp and span_is_verbatim(slug, f.get("pmid"), sp):
            cls, sub = exclusion_audit_class(slug, f.get("pmid"))
            o.setdefault("named_differences", []).append(
                {"trial": x["label"], "kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": f["rule_id"],
                 "screen_reason": f.get("reason"), "audit": {"class": cls, "subclass": sub},
                 "protocol_rule": protocol_rule_for(cfg, f["rule_id"], f.get("reason")) if cfg else None,
                 "registered_eligibility": cfg.get("eligibility_summary"), "pmid": f.get("pmid"), "span": sp,
                 "named_by": "acq/k-gap tracker (audit span), not the lane"})
            x["scope_difference"], x["blocker"] = o["named_differences"][-1], None
            o["open_gaps"] = [g for g in o.get("open_gaps") or [] if g != x["label"]]
            o["N_eligible"] = len(o.get("trials") or []) - len(o["named_differences"])
    for d in o.get("named_differences") or []:
        if d.get("kind") == "PROTOCOL_SCOPE_DIFFERENCE":
            sp = d.get("span") or exclusion_audit_span(slug, d.get("pmid"))
            if d.get("rule_id") and sp and span_is_verbatim(slug, d.get("pmid"), sp):
                keep.append(dict(d, span=sp, span_source=span_source_of(slug, d.get("pmid"), sp)))
                continue
            cls, sub = exclusion_audit_class(slug, d.get("pmid"))
            why = f"SCOPE_UNCITED:{d.get('rule_id')}" + (f" (audit {cls}:{sub})" if cls else " (not audited)")
        elif d.get("kind") in ("ESTIMAND_DIFFERENCE", "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS") and d.get("span") \
                and d.get("span_source") and (d.get("rule_id") or d.get("gate")):
            keep.append(d)
            continue
        elif d.get("kind") == "NOT_AN_INCLUDED_TRIAL" and d.get("rule_id") and d.get("span_source") \
                and span_is_verbatim(slug, d.get("pmid"), d.get("span")) \
                and span_is_verbatim(slug, o.get("comparator_pmid"), d.get("comparator_span")) \
                and d.get("comparator_stated_k") == sum(1 for x in o.get("trials") or [] if is_matched(x)):
            # both spans re-verified here, and the stated count still equals the matched count (harness/comparator_membership.py)
            keep.append(d)
            continue
        else:
            why = f"SCOPE_UNCITED:{d.get('kind')}"
        demoted.append(d.get("trial"))
        x = by_label.get(d.get("trial"))
        if x is not None:
            x["scope_difference"] = None
            x["blocker"] = why
            x["scope_demoted"] = {"was": {k: d.get(k) for k in ("kind", "rule_id", "gate", "protocol_rule", "pmid")},
                                  "why": why}
    # a trial neither matched, named nor listed as a gap (a lane file that lists no open_gaps) is ELIGIBLE: an open gap
    named_now = {d.get("trial") for d in keep}
    unlisted = [x.get("label") for x in o.get("trials") or [] if not is_matched(x)
                and x.get("label") not in named_now and x.get("label") not in (o.get("open_gaps") or [])
                and x.get("label") not in demoted]
    if not demoted and not unlisted:
        o["named_differences"] = keep
        return o
    o["named_differences"] = keep
    o["open_gaps"] = list(o.get("open_gaps") or []) + [t for t in demoted + unlisted if t not in (o.get("open_gaps") or [])]
    o["N_eligible"] = len(o.get("trials") or []) - len(keep)
    bl = Counter(x["blocker"] for x in o.get("trials") or [] if x.get("blocker") and not is_matched(x))
    o["blockers"] = dict(bl)
    o["top_blocker"] = bl.most_common(1)[0][0] if bl else None
    o["scope_demoted"] = demoted
    return o


def resolve_cited_letters(trials, comp_rows, rp, screened, co_map):
    """A comparator reference that is a LETTER / COMMENT about a trial is that trial: PubMed's own CommentOn link (ONE
    PMID, a report we hold) replaces the cited PMID in rp, with the letter kept as cited_as. Never by title."""
    for x, t in zip(trials, comp_rows):
        co = (co_map.get(str(rp[id(t)])) or {}).get("comment_on") or []
        if not x["in_our_pool"] and len(co) == 1 and co[0] in screened and co[0] != rp[id(t)]:
            x["cited_as"] = {"pmid": rp[id(t)], "kind": "LETTER_OR_COMMENT", "comment_on": co[0],
                             "source": "registry/comment_on.json (PubMed CommentsCorrections CommentOn)"}
            rp[id(t)] = co[0]


_CITE_CACHE: dict = {}


def comparator_acronym_citations(comp):
    """{ACRONYM: {pmid, ...}} from the comparator's OWN held JATS: an acronym the text DEFINES with a citation -- 'RALES
    (The Effect of Spironolactone on Morbidity ...) (<xref rid="B1">1</xref>)' -- names the cited reference, whose
    <pub-id pub-id-type="pmid"> is in the comparator's own reference list."""
    import glob
    if comp in _CITE_CACHE:
        return _CITE_CACHE[comp]
    out = {}
    d = os.path.join(ROOT, "cache", "comparators", str(comp or ""))
    fs = sorted(glob.glob(os.path.join(d, "*jats*.xml")) + glob.glob(os.path.join(d, "*europepmc_fulltext.xml")))
    for f in fs:
        if out:
            break
        x = open(f, encoding="utf-8", errors="replace").read()
        refs = {}
        for rid, body in re.findall(r'<ref id="([^"]+)"[^>]*>(.*?)</ref>', x, re.S):
            pm = re.findall(r'pub-id-type="pmid">\s*(\d+)', body)
            if len(pm) == 1:
                refs[rid] = pm[0]
        body = x.split("<ref-list", 1)[0]
        for m in re.finditer(r'(?<![A-Za-z0-9-])([A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)*)(?:\s*\([^()<]{0,300}\))?\s*\(?\s*'
                             r'<xref rid="([^"]+)" ref-type="bibr"', body):
            if refs.get(m.group(2)):
                out.setdefault(m.group(1), set()).add(refs[m.group(2)])
    _CITE_CACHE[comp] = out
    return out


def _smb_comparator(slug):
    import secondary_meta_build as smb
    return smb.comparator_pmid(slug)


def resolve_by_comparator_citation(comp_rows, comp):
    """A comparator trial with NO identity (pre-registry, acronym label: 'RALES1999', 'EPHESUS2003') takes the PMID its
    comparator's own text cites where it DEFINES that acronym -- exactly one cited reference, else nothing. Basis kept."""
    cites = comparator_acronym_citations(comp)
    if not cites:
        return
    for t in comp_rows:
        if t.get("pmids") or t.get("ncts"):
            continue
        core = t["label"].strip()
        for _ in range(3):        # trailing reference number, year, or a year glued to the acronym ('RALES1999')
            core = re.sub(r"\s*(?:[\[(]\s*\d+\s*[\])]|,?\s+(?:19|20)\d\d[a-z]?)\s*$", "", core)
            core = re.sub(r"(?<=[A-Za-z])(?:19|20)\d\d$", "", core)
        pm = cites.get(core.upper()) if core.upper() == core else cites.get(core)
        if pm and len(pm) == 1:
            t["pmids"] = sorted(pm)
            t["identity_basis"] = (t.get("identity_basis") or []) + [f"COMPARATOR_TEXT_DEFINES_ACRONYM_WITH_CITATION:{core}"]


def needs_seed(x):
    """A comparator trial whose record our own screen must see: not in our pool and not yet funnelled. Never keyed on
    the route: a COMPARATOR-only row (route UNVERIFIED) says nothing about what our screen does with the record
    (OSLER-1, pcsk9-mace 3 Oct: its spanned X3 exclusion vanished when the dual read gave it a comparator row)."""
    return not x.get("in_our_pool") and not x.get("seeded_funnel")


def scope_difference(x, cfg, slug=None):
    """A comparator trial we do not pool, NAMED: PROTOCOL_SCOPE_DIFFERENCE (our registered screen excludes it, rule
    cited) or ESTIMAND_DIFFERENCE (its only available result is a different estimand, gate cited). None when the
    trial is an open gap (it must then stay visible as NO_ROW, never be dropped)."""
    import re as _re
    f = x.get("seeded_funnel") or {}
    if f.get("stage") == "SCREENED_OUT":
        if not f.get("rule_id"):
            return None                     # a screen-out with no rule cited is a blocker, never a named difference
        if f["rule_id"] == "X-DOSE":
            # the ARM-OBJECT stage's rule: the exclusion audit re-runs screen_record only and cannot reproduce it (main
            # 3733b80a: O'Neil 2018 read SCREENED_OUT_UNAUDITED:X-DOSE). The trial's own record must state the dose.
            ad = arm_object_difference(x, cfg, slug)
            return dict(ad, rule_id="X-DOSE", screen_reason=f.get("reason")) if ad else None
        # NAMED only when the deterministic exclusion audit says the record STATES the excluding fact; a screener error
        # or a thin record is a BLOCKER to fix, never a scope difference (6 of the first audit's 57 were screener errors)
        cls, sub = exclusion_audit_class(slug, f.get("pmid"))
        if cls != "TRUE_SCOPE_DIFFERENCE":
            return None
        # ...and only WITH the record's words establishing it (span), verbatim in the held record
        sp = exclusion_audit_span(slug, f.get("pmid"))
        if not span_is_verbatim(slug, f.get("pmid"), sp):
            return None
        return {"kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": f["rule_id"], "screen_reason": f.get("reason"),
                "span": sp, "span_source": span_source_of(slug, f.get("pmid"), sp),
                "audit": {"class": cls, "subclass": sub},
                "protocol_rule": protocol_rule_for(cfg, f["rule_id"], f.get("reason")),
                "registered_eligibility": cfg.get("eligibility_summary"), "pmid": f.get("pmid")}
    ad = arm_object_difference(x, cfg, slug)
    if ad:
        return ad
    rb = x.get("registry_binding") or {}
    cands = [c for c in rb.get("candidates") or [] if c.get("gate") != "OUTCOME_NOT_NAMED"]
    ref = [c for c in cands if c.get("gate") == "ESTIMAND"]
    # ESTIMAND_DIFFERENCE only when EVERY registry outcome that names ours is a different estimand: an outcome that
    # names ours and failed another gate (ARMS) is an open gap, not a named difference
    if rb.get("state") == "REFUSED" and ref and len(ref) == len(cands):
        c = ref[0]
        return {"kind": "ESTIMAND_DIFFERENCE", "gate": "harness.extract.composite_component_mismatch",
                "rule_id": "GATE:composite_component_mismatch",
                "span": {"field": "outcome title", "text": c["title"]},
                "span_source": f"AACT snapshot {(c.get('snapshot') or {}).get('id')} outcome "
                               f"{(c.get('analysis') or {}).get('outcome_id')}",
                "reason": c["reason"], "registry_outcome": c["title"], "registry_arms": c["arms"],
                "registry_analysis": c["analysis"], "snapshot": c["snapshot"],
                "comparator_pooled_it_as": x.get("comparator_row")}
    return None


_DOSE = re.compile(r"(\d+(?:[.·]\d+)?)\s*mg\b", re.I)
_PRIMARY_AT_WEEK = re.compile(r"primary (?:end ?point|outcome|efficacy end ?point)\b[^.]{0,120}?\bweeks? (\d{1,3})\b", re.I)


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=\.)\s+(?=[A-Z])", text or "") if s.strip()]


def arm_object_difference(x, cfg, slug):
    """A comparator trial whose OWN held record states a different DOSE or a different primary TIMEPOINT than the
    protocol's registered arm object (cfg.arm_object.dose.required; primary_outcome.timepoint_weeks +/- tolerance):
    semaglutide-obesity-weight O'Neil 2018 (30122305) -- 'All treatment doses were delivered once-daily' at 0.05-0.4 mg
    (the protocol's estimand is 2.4 mg weekly) and 'The primary endpoint was percentage weight loss at week 52' (Week 68
    +/- 8). Named only when (a) the protocol states the requirement, (b) the record states the trial's own value in a
    verbatim sentence, and for dose (c) the required dose appears NOWHERE in the record and every stated dose of the
    drug differs. A record that is silent stays an open gap: silence is never a difference."""
    if x.get("in_our_pool"):
        return None
    fam = str(x.get("family") or "")
    pmid = (x.get("seeded_funnel") or {}).get("pmid") or (fam.replace("PMID ", "") if fam.startswith("PMID ") else None)
    rec = held_record(slug, pmid) if pmid else None
    if not rec:
        return None
    ab = rec.get("abstract") or ""
    ao = (cfg or {}).get("arm_object") or {}
    po = (cfg or {}).get("primary_outcome") or {}
    found = []
    dose = ao.get("dose") or {}
    req, drug = str(dose.get("required") or ""), str(dose.get("drug") or "")
    if req and drug and _DOSE.search(req):
        want = float(_DOSE.search(req).group(1).replace("·", "."))
        text = (rec.get("title") or "") + " " + ab
        stated = [(s, [float(m.group(1).replace("·", ".")) for m in _DOSE.finditer(s)])
                  for s in _sentences(ab) if drug.lower() in s.lower()]
        stated = [(s, ds) for s, ds in stated if ds]
        alld = [d for _s, ds in stated for d in ds]
        req_rx = re.escape(req).replace(r"\.", "[.·]").replace(r"\ ", r"\s*")
        if alld and want not in alld and not re.search(req_rx, text, re.I):
            s = max(stated, key=lambda t: len(t[1]))[0]
            found.append({"rule": f"arm_object.dose.required = {req} {drug}", "span": {"field": "abstract", "text": s},
                          "stated": sorted(set(alld))})
    tw, tol = po.get("timepoint_weeks"), po.get("timepoint_tolerance_weeks") or 0
    if tw:
        for s in _sentences(ab):
            m = _PRIMARY_AT_WEEK.search(s)
            if m and abs(int(m.group(1)) - int(tw)) > int(tol):
                found.append({"rule": f"primary_outcome.timepoint = Week {tw} (tolerance {tol} weeks)",
                              "span": {"field": "abstract", "text": s}, "stated": f"week {m.group(1)}"})
                break
    found = [f for f in found if span_is_verbatim(slug, pmid, f["span"])]
    if not found:
        return None
    return {"kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": "ARM_OBJECT", "gate": "g1_tracker.arm_object_difference",
            "protocol_rule": "; ".join(f["rule"] for f in found), "span": found[0]["span"],
            "also": [{"rule": f["rule"], "span": f["span"]} for f in found[1:]],
            "span_source": f"PMID {pmid} record abstract (held)", "stated": [f["stated"] for f in found],
            "registered_eligibility": (cfg or {}).get("eligibility_summary"), "pmid": pmid}


def blocker_class(x, slug):
    """WHY a comparator trial is an OPEN gap, as a class that can be fixed once for every topic it blocks:
      SCREENER_ERROR:<sub> / INSUFFICIENT_RECORD:<sub>   seeded record screened out; audit says our screen is wrong / thin
      SCREENED_OUT_UNAUDITED:<rule>                       seeded record screened out, audit has not classified it
      EXTRACTION:<reason_code>                             in our screen, no admissible number (the code says why)
      NOT_IN_SCREEN / NO_RECORD_HELD                       seeding never reached screening / no record fetched
      ESTIMAND_REGISTRY_ONLY                               only a different-estimand registry result exists
      IDENTITY_UNRESOLVED / <k-gap class>                  the comparator's label is not yet a trial identity"""
    f = x.get("seeded_funnel") or {}
    if f.get("stage") == "SCREENED_OUT":
        cls, sub = exclusion_audit_class(slug, f.get("pmid"))
        if cls in ("SCREENER_ERROR", "INSUFFICIENT_RECORD"):
            return f"{cls}:{sub}"
        return f"SCREENED_OUT_UNAUDITED:{f.get('rule_id')}"
    if f.get("stage") == "DECLARED_ABSENT":
        return f"EXTRACTION:{f.get('reason_code')}"
    va = x.get("via_report_absent")
    if f.get("stage") == "SCREENED_VIA_OTHER_REPORT" and va:
        held = {True: "", False: ":DECLARED_WITHOUT_FULL_TEXT", None: ""}[va.get("full_text_held")]
        return f"EXTRACTION:{va['code']}:VIA_OTHER_REPORT{held}"
    if f.get("stage") in ("NOT_IN_SCREEN", "INCLUDED_NOT_IN_PRIMARY", "SCREENED_VIA_OTHER_REPORT"):
        return f["stage"]
    if x.get("our_refusal") == "NO_RECORD_HELD":
        return "NO_RECORD_HELD"
    if x.get("absent_code"):
        return f"EXTRACTION:{x['absent_code']}"
    if x["family"] is None:
        return "IDENTITY_UNRESOLVED" if (x.get("gap_class") or "").startswith("UNRESOLVED") else (x.get("gap_class") or "UNKNOWN")
    return x.get("gap_class") or "UNKNOWN"


_FT_INDEX = None


def full_text_held(pmid):
    """True/False from outputs/k_gap/fulltext_index.json (bytes > 0); None when the index is absent -- unknown, not 'no'."""
    global _FT_INDEX
    if _FT_INDEX is None:
        p = os.path.join(OUT, "fulltext_index.json")
        _FT_INDEX = _j(p) if os.path.exists(p) else {}
    if not _FT_INDEX:
        return None
    return bool((_FT_INDEX.get(str(pmid)) or {}).get("bytes"))


def comparator_findings(trials, comp):
    """Findings ABOUT the comparator's own rows, typed, each with where it sits and what it rests on."""
    out = []
    for x in trials:
        d, cr = x.get("scope_difference") or {}, x.get("comparator_row") or {}
        an = d.get("registry_analysis") or {}
        if d.get("kind") == "ESTIMAND_DIFFERENCE" and cr.get("effect") and an.get("param_value"):
            same = all(sm._eq_printed(cr.get(a), an.get(b)) for a, b in (("effect", "param_value"),
                                                                       ("lower", "ci_lower"), ("upper", "ci_upper")))
            if same:
                out.append({"finding": "COMPARATOR_POOLED_A_DIFFERENT_ESTIMAND", "trial": x["label"], "comparator": comp,
                            "comparator_row": cr, "registry_outcome": d.get("registry_outcome"),
                            "registry_analysis": an, "snapshot": d.get("snapshot"), "gate_reason": d.get("reason"),
                            "basis": "the comparator's printed row equals, at its printed precision, the registry result "
                                     "of the composite our gate refuses for this topic"})
    for x in trials:
        if x.get("disagreement_side", "") and str(x["disagreement_side"]).startswith("SECONDARY_WRONG"):
            out.append({"finding": "COMPARATOR_ROW_DIFFERS_FROM_TRIAL_REPORT", "trial": x["label"], "comparator": comp,
                        "comparator_row": x.get("comparator_row"), "trial_report": x.get("our_value"),
                        "basis": x["disagreement_side"]})
        for f in x.get("comparator_row_findings") or []:
            if not isinstance(f, dict):           # a legacy string finding (lane-written) is typed, never a crash
                f = {"finding": str(f).partition(":")[0].strip(), "detail": str(f)}
            out.append({"finding": f.get("finding"), "trial": x["label"], "comparator": comp,
                        "comparator_row": x.get("comparator_row"),
                        "detail": f.get("printed_vs_arm_derived") or f.get("detail")})
        at = x.get("analysis_set_attribution") or {}
        if at.get("state") in ("REPRODUCED", "NOT_REPRODUCED") and at.get("ours") != (at.get("reproduced_by") or at.get("nearest")):
            # the comparator's row is (or is nearest to) a DIFFERENT analysis set of the same trial report than the one our
            # registered estimand pools (harness/analysis_set.py): a scope difference on the analysis-set axis, typed
            out.append({"finding": ("COMPARATOR_ROW_IS_A_DIFFERENT_ANALYSIS_SET" if at["state"] == "REPRODUCED"
                                    else "COMPARATOR_ROW_NEAREST_TO_A_DIFFERENT_ANALYSIS_SET"),
                        "trial": x["label"], "comparator": comp, "comparator_row": x.get("comparator_row"),
                        "ours": at.get("ours"), "theirs": at.get("reproduced_by") or at.get("nearest"),
                        "reproduced": at["state"] == "REPRODUCED", "per_set": at.get("per_set")})
    return out


def analysis_set_attribution(slug, cfg, x):
    """Which analysis set of the trial's held report each side's number comes from (harness/analysis_set.py)."""
    from harness import analysis_set
    pmid = str((x.get("family") or "")).replace("PMID ", "").strip()
    rp = os.path.join(ROOT, "cache", slug, "records.json")
    recs = {str(r.get("id")): r for r in (_j(rp).get("records") or [])} if os.path.exists(rp) else {}
    rec = recs.get(pmid) or {}
    inc = cfg.get("include") or {}
    sets = analysis_set.labelled_counts(rec.get("abstract") or "", inc.get("intervention_any") or [],
                                        list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or []),
                                        (cfg.get("primary_outcome") or {}).get("keywords") or [])
    res = analysis_set.attribute(x.get("comparator_row") or {}, sets)
    ov = x.get("our_value") or {}
    ours = next((s["analysis_set"] for s in sets if (s["treatment"]["events"], s["treatment"]["n"], s["control"]["events"],
                                                     s["control"]["n"]) == (ov.get("events_t"), ov.get("n_t"),
                                                                            ov.get("events_c"), ov.get("n_c"))), None)
    return dict(res, ours=ours, report_pmid=pmid or None)


def our_value_from_row(t):
    """Our value for one pooled trial, from its pool row: effect + CI, or the 2x2; None when neither is there."""
    if t.get("effect") is not None and t.get("ci_low") is not None:
        return {"measure": (t.get("scale") or "").upper(), "effect": str(t["effect"]), "lower": str(t["ci_low"]),
                "upper": str(t["ci_high"]), "source": f"our held-source pool {t.get('id')} ({t.get('provenance')})"}
    if t.get("ai") is not None:
        return {"measure": "RR", "events_t": t["ai"], "n_t": t["n1i"], "events_c": t["ci"], "n_c": t["n2i"],
                "source": f"our held-source pool {t.get('id')} ({t.get('provenance')})"}
    # a continuous outcome pooled from ARM means / SDs / Ns (esketamine MADRS): the value is that mean difference
    if None not in (t.get("mean1"), t.get("sd1"), t.get("nc1"), t.get("mean2"), t.get("sd2"), t.get("nc2")):
        return {"measure": "MD", "mean_t": str(t["mean1"]), "sd_t": str(t["sd1"]), "n_t": int(t["nc1"]),
                "mean_c": str(t["mean2"]), "sd_c": str(t["sd2"]), "n_c": int(t["nc2"]),
                "source": f"our held-source pool {t.get('id')} ({t.get('provenance')})"}
    return None


def with_identity_chain(T):
    """k-gap rows with NO identity take the identity chain's RESOLVED identity (outputs/k_gap/identity_chain.json:
    label -> PMID -> NCT through AACT study_references, own publications only), basis recorded. A resolved trial of
    ANOTHER agent becomes drug OTHER_AGENT (reported in other_agent_units, out of a drug-specific topic's N)."""
    import copy
    ip = os.path.join(OUT, "identity_chain.json")
    if not os.path.exists(ip):
        return T
    res = _j(ip).get("results") or {}
    T = copy.deepcopy(T)
    for t in T["trials"]:
        v = res.get(f"{t['slug']}::{t['label']}")
        if v and v.get("state") == "COMMENT_ON" and t.get("pmids") == [v.get("from")]:
            # the unit's only report is a Letter / Comment: it names the article it comments on (PubMed CommentOn)
            t["pmids"] = [v["pmid"]]
            t["identity_basis"] = list(t.get("identity_basis") or []) + [f"IDENTITY_CHAIN:COMMENT_ON:{v['from']}->{v['pmid']}"]
            t["status"] = "RESOLVED_BY_CHAIN"
            continue
        if (v and v.get("state") == "AMBIGUOUS" and str(v.get("scope") or "").startswith("OTHER_AGENT")
                and not t.get("ncts") and not t.get("pmids") and t.get("drug") != "DRUG_MATCH"):
            # which paper is the report is unresolved, but EVERY self-naming title names another agent and none the
            # topic's: the unit is another agent's trial (out of a drug-specific topic's N), its identity left open
            t["drug"] = "OTHER_AGENT"
            t["identity_basis"] = list(t.get("identity_basis") or []) + [
                f"IDENTITY_CHAIN:{v.get('basis')}:AMBIGUOUS_REPORT_UNANIMOUS_{v['scope']}"]
            continue
        if not v or v.get("state") != "RESOLVED" or t.get("ncts") or t.get("pmids"):
            continue
        t["ncts"] = [v["nct"]] if v.get("nct") else []
        t["pmids"] = [v["pmid"]] if v.get("pmid") else []
        t["identity_basis"] = [f"IDENTITY_CHAIN:{v.get('basis')}"]
        t["status"] = "RESOLVED_BY_CHAIN"
        if str(v.get("scope") or "").startswith("OTHER_AGENT"):
            t["drug"] = "OTHER_AGENT"
    return T


def attach_forest_reader_provenance(o, slug):
    """A LANE file's comparator rows (tocilizumab: the lane's own counts, no per-row location) take the provenance of
    the forest-reader lane's DUAL-MODEL read of the SAME comparator figure -- only for a row that joins exactly one
    forest-reader row (the build's family join) AND prints the same four counts (the values are verified identical,
    never replaced). The figure's acceptance (rows reproduce its printed pool) is then this topic's G1-R. Returns the
    number of rows given provenance."""
    import secondary_meta_build as smb
    comp = str(o.get("comparator_pmid") or "")
    rows, used = lane_comparator_rows(slug, comp, [{"id": x["label"], "label": x["label"], "acronyms": [], "author_year": None}
                                                   for x in o.get("trials") or []])
    acc = next((u for u in used if (u.get("acceptance") or {}).get("state") == "ACCEPTED"), None)
    if not acc:
        return 0
    n = 0
    by = {}
    for r in rows:
        if r.family_id:
            by.setdefault(r.family_id, []).append(r)
    for x in o.get("trials") or []:
        cr = x.get("comparator_row") or {}
        if not cr or x.get("comparator_row_provenance"):
            continue
        want = tuple(cr.get(k) for k in ("events_t", "n_t", "events_c", "n_c"))
        same = [r for r in by.get(x["label"], []) if (r.events_t, r.n_t, r.events_c, r.n_c) == want and None not in want]
        if len(same) == 1:
            r = same[0]
            x["comparator_row_provenance"] = {"meta_pmid": r.meta_pmid, "location": r.location, "digest": r.source_digest,
                                              "read": r.provenance, "row_label": r.trial_label,
                                              "verified": "the forest-reader dual read prints the same counts"}
            n += 1
    if not (o.get("g1r_reproduction") or {}).get("state") == "REPRODUCED":
        o["g1r_reproduction"] = {"state": "REPRODUCED", "rows": acc.get("rows"),
                                 "methods": (acc.get("acceptance") or {}).get("methods_reproducing"),
                                 "where": f"figure {acc.get('figure')} (g1/forest-reader {str(acc.get('commit'))[:9]}, dual-model)",
                                 "control_basis": f"FOREST_READER_ACCEPTANCE ({(acc.get('acceptance') or {}).get('pooled_anchor')})"}
    return n


def lane_comparator_rows(slug, comp, ours):
    """The COMPARATOR's own per-trial rows read by another lane (outputs/k_gap/g1_comparator_rows.json lists the
    sources: g1/forest-reader's dual-model figure reads), taken only where that lane ACCEPTED the figure for THIS
    comparator, pinned by branch commit + blob sha256, and joined to our trials by the build's family join. They are
    comparator rows: they feed per-trial agreement and the same-trials comparison, and never count toward G1."""
    import hashlib
    import subprocess
    import secondary_meta_build as smb
    sp = os.path.join(OUT, "g1_comparator_rows.json")
    out, used = [], []
    for src in (_j(sp) if os.path.exists(sp) else []):
        if src.get("format", "forest_reader_v1") != "forest_reader_v1":
            continue                      # the listing also names the lane's row identity map (not rows)
        try:
            commit = subprocess.run(["git", "rev-parse", f"origin/{src['branch']}"], cwd=ROOT, capture_output=True,
                                    text=True, stdin=subprocess.DEVNULL, check=True).stdout.strip()
            b = subprocess.run(["git", "show", f"{commit}:{src['path']}"], cwd=ROOT, capture_output=True,
                               stdin=subprocess.DEVNULL, check=True).stdout
        except subprocess.CalledProcessError:
            continue
        res = (json.loads(b.decode("utf-8")).get("results") or {}).get(slug) or {}
        if res.get("state") != "ACCEPTED" or str(res.get("pmid")) != str(comp):
            continue
        fam = smb.family_of_factory(ours)
        for d in res.get("secondary_rows") or []:
            r = _row(d)
            r.family_id = fam(r)
            out.append(r)
        used.append({"branch": src["branch"], "commit": commit, "path": src["path"],
                     "acceptance": {k: (res.get("acceptance") or {}).get(k) for k in ("state", "methods_reproducing",
                                                                                     "pooled_anchor", "problems")},
                     "figure": (res.get("figure") or {}).get("fig_id"), "pooled_agreed": res.get("pooled_agreed"),
                     "sha256": hashlib.sha256(b).hexdigest(), "rows": len(res.get("secondary_rows") or []),
                     "joined": sum(1 for r in out if r.family_id)})
    return out, used


def is_pooled(mine, pooled_ids):
    """Pool MEMBERSHIP, independent of how our value is stored (effect+CI, 2x2, or arm means for an MD)."""
    return bool(mine and str(mine.get("id")) in pooled_ids)


def report_pmid(t, shown=None):
    """The trial's RESULT-typed report (k_gap_identity_reader2.shown_pmid), never blindly pmids[0]: a trial's first
    linked PMID can be a design paper or an animal study (ELIXA's is a rat study)."""
    if shown is None:
        import k_gap_identity_reader2 as r2
        shown = r2.shown_pmid
    try:
        p = shown(t)
    except Exception:  # noqa: BLE001 - a resolver failure falls back to the first id, recorded by the caller
        p = None
    p = p or next((q for q in (t.get("pmids") or []) if str(q).isdigit()), None)
    return str(p) if p else None


def name_letter_units_by_comment_on(slug, cfg, trials, rev):
    """A comparator unit that is a LETTER / COMMENT about one article stands for that article (kgap/comment_on.py:
    PubMed CommentOn, recorded with its XML sha256). It is named a PROTOCOL_SCOPE_DIFFERENCE only when OUR served screen
    excluded that article under a rule AND the exclusion audit classes the article's exclusion TRUE_SCOPE_DIFFERENCE with
    a span verbatim in the article's held record -- the span and rule are the ARTICLE's, never the letter's words
    (sglt2-primary-prevention-hf: 'Isreb (19)', NEJM letter 31509682 on CREDENCE 30990260, screened out X2 'nephropathy')."""
    import re
    from kgap import comment_on as co
    import k_gap_exclusion_audit as au
    ledger = {str(r.get("id")): r for r in ((rev or {}).get("screening") or {}).get("records", [])}
    for x in trials:
        # g1/finish-line's CommentOn re-point (registry/comment_on.json -> x['cited_as']) may have named the unit already
        # by the article's screen exclusion; this stricter rule (one resolved edge, row bound by the article's own patient
        # count, audit rule == served rule: NR-C24) then still runs and, when it holds, replaces that naming with its
        # row-bound one (consolidation 2026-10-04: both lanes built the letter -> article edge)
        via_cited = bool((x.get("cited_as") or {}).get("comment_on")) and bool(x.get("scope_difference"))
        if is_matched(x) or (x.get("scope_difference") and not via_cited):
            continue
        pmid = str(x.get("family") or "").replace("PMID ", "").strip()
        rec = held_record(slug, pmid) or {}
        pts = [str(p).lower() for p in rec.get("pubtypes") or []]
        if not any(t in pts for t in ("letter", "comment", "editorial")) or any("randomized controlled trial" in p for p in pts):
            continue
        rco = co.record(pmid)
        targets = rco.get("comment_on") or []
        # exactly ONE CommentOn relationship, resolved (an unresolved second edge makes the target ambiguous: NR-C24)
        if len(targets) != 1 or rco.get("comment_on_unresolved"):
            continue
        art = targets[0]
        led, arec = ledger.get(art) or {}, held_record(slug, art)
        if led.get("decision") != "exclude" or not led.get("rule_id") or not arec:
            continue
        # the comparator's ROW must be the article's trial: its arm sizes sum to a patient count the article itself states
        # (a comment link is a relationship, not trial identity -- NR-C24; Isreb row 2202 + 2199 = 4401, CREDENCE: '4401
        # patients had undergone randomization')
        row = x.get("comparator_row") or {}
        try:
            total = int(row.get("n_t")) + int(row.get("n_c"))
        except (TypeError, ValueError):
            continue
        tot_rx = re.compile(r"(?<![\d.,])" + "{:,}".format(total).replace(",", r"[,  ]?") + r"(?![\d.,]\d)")
        bind = next(((f, m.group(0)) for f in ("abstract", "title") for m in [tot_rx.search(arec.get(f) or "")] if m), None)
        if not bind:
            continue
        cls, sub, base = au.classify(arec, cfg)
        sp = (base or {}).get("span")
        # the served screen's rule and the audit's re-screen must AGREE on the excluding rule (NR-C24)
        if cls != "TRUE_SCOPE_DIFFERENCE" or not sp or not span_is_verbatim(slug, art, sp) or                 (base or {}).get("rule_id") != led["rule_id"]:
            continue
        x["scope_difference"] = {
            "kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": led["rule_id"], "screen_reason": led.get("reason"),
            "audit": {"class": cls, "subclass": sub}, "protocol_rule": protocol_rule_for(cfg, led["rule_id"], led.get("reason")),
            "registered_eligibility": cfg.get("eligibility_summary"), "pmid": art, "span": sp,
            "span_source": span_source_of(slug, art, sp) + f" -- the comparator unit is PMID {pmid} "
                           f"({', '.join(rec.get('pubtypes') or [])}), which comments on PMID {art}",
            "via_comment_on": {"unit_pmid": pmid, "comment_on": art, "source": rco.get("source"),
                               "xml_sha256": rco.get("xml_sha256"), "record": "outputs/k_gap/comment_on.json"},
            "row_binding": {"total": total, "article_field": bind[0], "article_states": bind[1],
                            "basis": "comparator row n_t + n_c equals a patient count stated in the article's held record"}}
        x["blocker"] = None


def name_reference_seeds_outside_membership(slug, comp, trials, T):
    """A REFERENCE-SEEDED comparator unit that the comparator's OWN abstract places outside its stated membership is
    named NOT_AN_INCLUDED_TRIAL (harness/comparator_membership.py: stated k == matched k, and the unit's record says it
    pools several trials; both spans verbatim in held records). Every other unmatched trial is left as it was."""
    from harness import comparator_membership as cmb
    k_matched = sum(1 for x in trials if is_matched(x))
    crec = held_record(slug, comp) or {}
    for x in trials:
        if is_matched(x) or x.get("scope_difference"):
            continue
        pmid = str(x.get("family") or "").replace("PMID ", "").strip()
        if not pmid.isdigit():
            continue
        row = next((t for t in T["trials"] if t["slug"] == slug and pmid in (t.get("pmids") or [])), None)
        urec = held_record(slug, pmid) or {}
        d = cmb.not_an_included_trial(crec.get("abstract") or "", k_matched, urec.get("abstract") or "",
                                      (row or {}).get("unit_source"), unit_pubtypes=urec.get("pubtypes") or [],
                                      unit_title=urec.get("title") or "", unit_pmid=pmid,
                                      matched_pmids=[str(m.get("family") or "").replace("PMID ", "").strip()
                                                     for m in trials if is_matched(m)])
        if not d:
            continue
        x["scope_difference"] = dict(d, pmid=pmid, span_source=span_source_of(slug, pmid, d["span"]),
                                     comparator_span_source=span_source_of(slug, comp, d["comparator_span"]))
        x["blocker"] = None


_STATED_K = re.compile(r"\b(\d+|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(?:phase\s*(?:3|III)\s+|"
                       r"randomi[sz]ed\s+(?:controlled\s+)?|placebo-controlled\s+|eligible\s+)*(?:clinical\s+)?trials\b", re.I)


def comparator_stated_k(comp):
    """(k, span) when the comparator's OWN held abstract states how many trials its pooled analysis has ('6 phase 3
    trials including a total of 27,023 patients'), else (None, None). Read from cache/comparators/<pmid>/*pubmed_efetch.xml
    or the held JATS abstract; the FIRST such statement only, never a sum."""
    import glob
    import html
    d = os.path.join(ROOT, "cache", "comparators", str(comp or ""))
    for fp in sorted(glob.glob(os.path.join(d, "*pubmed_efetch.xml")) + glob.glob(os.path.join(d, "*jats.xml"))):
        x = open(fp, encoding="utf-8", errors="replace").read()
        ab = " ".join(re.findall(r"<(?:Abstract|abstract)[^>]*>.*?</(?:Abstract|abstract)>", x, re.S))
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", ab)))
        m = _STATED_K.search(t)
        if m:
            w = m.group(1).lower()
            return (int(w) if w.isdigit() else _NUMW[w]), {"field": "comparator abstract", "text": m.group(0),
                                                           "source": os.path.relpath(fp, ROOT).replace(os.sep, "/")}
    return None, None


def whole_pool_comparison(o, printed_k=None):
    """When EVERY comparator trial is matched and the comparator prints no per-trial rows (an IPD / network meta), the
    'same trials' ARE both whole pools: compare our pooled result with the comparator's printed one, labelled as such,
    with both methods recorded (they may differ: e.g. our PM+HKSJ vs an IPD model). Also when the comparator's own
    abstract STATES its pooled trial count and that count equals our pool's k, our matched k and the eligible N: the
    named differences are then outside its pool (doac-vte: '6 phase 3 trials'; the named 24081972 is a pooled bleeding
    analysis, not a trial). Otherwise None."""
    st = o.get("same_trials") or {}
    ours, comp = o.get("ours") or {}, o.get("comparator") or {}
    if st.get("state") in ("POOLED", "ONE_SHARED_TRIAL", "ONE_COMPARABLE_TRIAL", "MEASURE_DIFFERENCE"):
        return None
    nd = o.get("named_differences") or []
    k = o["k_matched"]
    sk, sspan = comparator_stated_k(o.get("comparator_pmid")) if nd else (None, None)
    all_shared = k == o["N_comparator_trials"] and not nd and ours.get("k") == o["N_comparator_trials"]
    stated_same = sk is not None and sk == k == o["N_eligible"] == ours.get("k") and not o["open_gaps"]
    # g1/sglt2 lane: every named difference is a reference seed OUTSIDE the comparator's own stated membership
    # (NOT_AN_INCLUDED_TRIAL) -> the comparator's pool is exactly the matched set
    n_set = o["N_comparator_trials"] - len(nd)
    outside_membership = bool(nd) and all(d.get("kind") == "NOT_AN_INCLUDED_TRIAL" for d in nd) \
        and k == n_set == ours.get("k")
    # acq/k-gap f34580f9: the comparator's own text prints exactly one pooled k and k IS our matched set
    by_k = bool(printed_k) and printed_k == k == ours.get("k") and not o.get("ours_not_in_comparator")
    # all four admission paths kept (consolidated 2026-10-04)
    if not (all_shared or stated_same or outside_membership or by_k):
        return None
    if None in (ours.get("estimate"), ours.get("ci_low"), ours.get("ci_high"), comp.get("estimate"),
                comp.get("ci_low"), comp.get("ci_high")):
        return None
    basis = ("ALL_TRIALS_SHARED_WHOLE_POOLS (comparator prints no per-trial rows)" if all_shared else
             f"COMPARATOR_STATES_ITS_POOL_K ({sk} = our matched k = eligible N; named differences are outside its pool)"
             if stated_same else "NAMED_DIFFERENCES_OUTSIDE_COMPARATOR_MEMBERSHIP (the comparator's pool is the matched set)"
             if outside_membership else f"COMPARATOR_STATES_K={printed_k}=OUR_MATCHED_SET (comparator prints no per-trial rows)")
    m = (ours.get("scale") or "").upper()
    if m != (comp.get("scale") or "").upper():
        # a NAMED measure difference (our HR vs their RR/OR): never converted; passes RESULT_AGREES only on the SAME
        # conclusion about the null. The event-total check rides beside it, read-only.
        o_ = {k_: ours[k_] for k_ in ("estimate", "ci_low", "ci_high")}
        t_ = {k_: comp[k_] for k_ in ("estimate", "ci_low", "ci_high")}
        same = _concl(o_, m) == _concl(t_, (comp.get("scale") or "").upper())
        return {"state": "MEASURE_DIFFERENCE", "basis": basis, "k": k, "stated_k_span": sspan,
                "ours": dict(o_, measure=ours.get("scale")), "theirs": dict(t_, measure=comp.get("scale")),
                "outcome_check": whole_pool_event_check(o),
                "verdict": {"verdict": "MEASURE_DIFFERENCE_SAME_CONCLUSION" if same else "DIFFERENT_CONCLUSION",
                            "basis": "our pool is on hazard ratios; the comparator pooled a ratio of risks/odds: never converted"}}
    o_ = {k_: ours[k_] for k_ in ("estimate", "ci_low", "ci_high")}
    t_ = {k_: comp[k_] for k_ in ("estimate", "ci_low", "ci_high")}
    return {"state": "POOLED", "basis": basis, "stated_k_span": sspan,
            "k": o["k_matched"], "measure": m, "method": "ours: served pool method; theirs: as printed",
            "ours": {k: round(v, 4) for k, v in o_.items()}, "theirs": t_, "verdict": result_verdict(o_, t_, m)}


def served_topics():
    """Every SERVED topic (docs/reviews/<slug>/review.json): the tracker's denominator. A topic must never be missing
    from the tracker silently (denosumab-vertebral-fracture was, 3 Oct: its comparator lists no enumerable trial)."""
    d = os.path.join(ROOT, "docs", "reviews")
    return sorted(s_ for s_ in os.listdir(d) if os.path.exists(os.path.join(d, s_, "review.json")))


def g1_status(o):
    """G1 MATCHED, by the goal's definition, as typed criteria (all must hold):
      ALL_ELIGIBLE_MATCHED   every eligible comparator trial is in our pool (k_matched == N_eligible, no open gap)
      MATCHED_ARE_VERIFIED   every matched trial has a counted route (PRIMARY / TWO_SOURCE), comparator-only never
      RESULT_AGREES          on the same trials, ours vs the comparator's rows: verdict AGREE
      DIVERGENCES_NAMED      every non-match is a named difference citing its rule/gate AND a source span, and
                             every per-trial disagreement carries the side it falls on
    Always reported beside the state: excluded_by_scope = how many comparator trials left the eligible denominator,
    of the comparator's N (a G1_MATCHED on 2 eligible of 9 is a different claim from 9 of 9)."""
    tr = o["trials"]
    nd = o.get("named_differences") or []
    N = o.get("N_comparator_trials", len(tr))
    excl = {"n": len(nd), "of_comparator_N": N,
            "by_kind": dict(Counter(d.get("kind") for d in nd)),
            "trials": [f"{d.get('trial')} [{d.get('rule_id') or d.get('gate')}]" for d in nd]}
    if not o.get("N_comparator_trials", len(tr)):
        cs = o.get("comparator_set") or {}
        return {"state": "COMPARATOR_NOT_ENUMERATED", "criteria": {}, "unmet": ["COMPARATOR_TRIAL_LIST"],
                "excluded_by_scope": excl,
                "why": f"the comparator's trial list could not be enumerated from open sources "
                       f"({cs.get('state')}; tried {cs.get('sources_tried')})"}
    v = ((o.get("same_trials") or {}).get("verdict") or {}).get("verdict")
    dis = [x for x in tr if str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE")]
    readers_differ = [x["label"] for x in tr if is_matched(x)
                      and (x.get("comparator_row_readings") or {}).get("state") == "READERS_DIFFER"]
    crit = {
        "ALL_ELIGIBLE_MATCHED": o["N_eligible"] > 0 and o["k_matched"] == o["N_eligible"] and not o["open_gaps"],
        "MATCHED_ARE_VERIFIED": all((x["route"] in ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE") or str(x["route"]).startswith("SWEEP_"))
                                    and x.get("g1_countable", True) for x in tr if is_matched(x)),
        # a READERS_DIFFER comparator row is never resolved by a pick: the result agrees only if the verdict is the
        # SAME under every reading (same_trials.readers_agree_on_verdict), else it is unmet until the readers resolve
        # AGREE, or a NAMED measure difference (our HRs vs their RR/OR, never converted) with the same conclusion
        "RESULT_AGREES": v in ("AGREE", "MEASURE_DIFFERENCE_SAME_CONCLUSION")
                         and (not readers_differ or (o.get("same_trials") or {}).get("readers_agree_on_verdict") is True),
        "DIVERGENCES_NAMED": all((d.get("protocol_rule") or d.get("gate")) and (d.get("span") or {}).get("text")
                                 for d in nd)
                             and all(x.get("disagreement_side") for x in dis),
    }
    return {"state": "G1_MATCHED" if all(crit.values()) else "NOT_YET", "criteria": crit,
            "unmet": [k for k, ok in crit.items() if not ok], "excluded_by_scope": excl,
            "result_blocker": None if crit["RESULT_AGREES"] else result_blocker(o, readers_differ)}


def result_blocker(o, readers_differ=()):
    """WHY RESULT_AGREES is unmet, typed (never a bare NOT_YET): the comparator prints no result for the outcome; the
    measures differ (per trial or whole pool); fewer than two comparable pairs (and why each pair is missing); a
    different result -- with the comparator rows our primaries contradict, which would cause it; or readers differ."""
    st = o.get("same_trials") or {}
    comp = o.get("comparator") or {}
    tr = o.get("trials") or []
    wrong = [x["label"] for x in tr if str(x.get("disagreement_side") or "").startswith("SECONDARY_WRONG")]
    if comp.get("estimate") is None:
        return {"code": "COMPARATOR_PRINTS_NO_RESULT_FOR_OUTCOME",
                "detail": "the comparator's typed result for this outcome is empty: nothing to agree with"}
    if readers_differ:
        return {"code": "READERS_DIFFER", "trials": list(readers_differ)}
    state = st.get("state")
    v = (st.get("verdict") or {}).get("verdict")
    if state == "MEASURE_DIFFERENCE":
        # upstream f34580f9: our HRs vs their RR/OR pass only on the SAME conclusion about the null
        return {"code": "MEASURE_DIFFERENCE:" + str(v), "basis": st.get("basis"), "k": st.get("k"),
                "ours": st.get("ours"), "theirs": st.get("theirs"),
                "pairs_with_a_different_conclusion": [d["trial"] for d in st.get("measure_differences") or []
                                                      if not d.get("same_conclusion")],
                "stated_k_span": st.get("stated_k_span"), "outcome_check": st.get("outcome_check")}
    if state in ("ONE_SHARED_TRIAL", "ONE_COMPARABLE_TRIAL"):
        return {"code": "ONE_TRIAL_RESULT:" + str(v), "trial": st.get("trial"), "ours": st.get("ours"),
                "theirs": st.get("theirs"), "comparator_rows_contradicted_by_primary": wrong}
    if state == "ROW_NOT_COMPARABLE":
        return {"code": "ONE_SHARED_TRIAL_NOT_COMPARABLE", "k": st.get("k")}
    if state == "WHOLE_POOL_MEASURE_DIFFERS":
        return {"code": "MEASURE_DIFFERS_WHOLE_POOL", "ours": st.get("ours"), "theirs": st.get("theirs"),
                "ours_result": st.get("ours_result"), "theirs_result": st.get("theirs_result"), "basis": st.get("basis"),
                "stated_k_span": st.get("stated_k_span")}
    if state == "MIXED_MEASURES":
        return {"code": "MEASURE_DIFFERS_PER_TRIAL", "measures": st.get("measures"), "k_pairs": st.get("k"),
                "comparator_rows_contradicted_by_primary": wrong}
    if state == "FEWER_THAN_2_SHARED_TRIALS":
        why = Counter(str(x.get("agreement_with_comparator_row") or "")
                      for x in tr if is_matched(x) and not str(x.get("agreement_with_comparator_row") or "").startswith("AGREE"))
        return {"code": "FEWER_THAN_2_COMPARABLE_PAIRS", "k_pairs": st.get("k"), "matched_without_a_pair": dict(why)}
    if state == "POOLED":
        v = (st.get("verdict") or {}).get("verdict")
        return {"code": "RESULT_DIFFERS:" + str(v), "verdict": st.get("verdict"),
                "comparator_rows_contradicted_by_primary": wrong,
                "note": ("the comparator rows our primaries contradict are in the same-trials pool" if wrong else None)}
    return {"code": str(state or "NO_SAME_TRIALS_COMPARISON")}


_ELIG_STAGES = ("INCLUDED_NOT_IN_PRIMARY", "DECLARED_ABSENT", "POOLED")
_SCREEN_PROPS = ("screening_excluded", "screening_excluded_x1", "screening_excluded_reader2",
                 "screening_excluded_x1_reader2", "k_gap_screen_recheck", "k_gap_screen_rrl")
_READER2 = re.compile(r"reader2|#r2\b")


def two_reader_readings(slug, pmids):
    """Every VERIFIED screening reading recorded for these PMIDs of this topic (registry/model_proposals: the pilot's
    screening_excluded* tasks, k_gap_screen_recheck, k_gap_screen_rrl), with which reader made it."""
    out = []
    want = {f"{slug}::pmid:{p}" for p in pmids or []} | {f"{slug}::rrl:{p}" for p in pmids or []}
    for task in _SCREEN_PROPS:
        pp = os.path.join(ROOT, "registry", "model_proposals", task + ".json")
        if not os.path.exists(pp):
            continue
        d = _j(pp)
        for it in (d.get("items") or []) + (d.get("rows") or []):
            if it.get("item_id") not in want:
                continue
            v = it.get("verification") or {}
            if v.get("state", "VERIFIER_PASS") != "VERIFIER_PASS" or not v.get("model_decision"):
                continue
            rd = it.get("reader") or ("READER_2" if _READER2.search(task + " " + str(it.get("batch") or "")) else "READER_1")
            out.append({"task": task, "reader": rd, "model_decision": v.get("model_decision"),
                        "agreement": str(v.get("agreement") or "")[:60], "record_id": it.get("record_id")})
    return out


def two_readers_eligible(readings):
    """Both readers (reader 1 AND reader 2, two models) judged ELIGIBLE on verified quotes, and no verified reading says
    INELIGIBLE. One reader, or any dissent, is not enough to set our screen's exclusion aside."""
    dec = {}
    for r in readings:
        dec.setdefault(r["reader"], set()).add(r["model_decision"])
    if any("INELIGIBLE" in v for v in dec.values()):
        return False
    return {"READER_1", "READER_2"} <= {k for k, v in dec.items() if v == {"ELIGIBLE"}}


def screen_eligibility(x, rec, pmid, readings):
    """Typed, per comparator trial outside our pool: what OUR screen says. rec = our screen's own decision record for the
    trial's report (None when the report never entered it); x['seeded_funnel'] = the decision when its held record was
    seeded through our unchanged build. ELIGIBLE / NOT_ELIGIBLE (rule + reason) / NOT_ASSESSED."""
    if x.get("in_our_pool"):
        return {"state": "ELIGIBLE", "basis": "POOLED"}
    f = x.get("seeded_funnel") or {}
    if rec is not None and rec.get("decision") == "include":
        return {"state": "ELIGIBLE", "basis": "OUR_SCREEN_INCLUDE", "pmid": pmid, "rule_id": rec.get("rule_id")}
    if f.get("stage") in _ELIG_STAGES:
        return {"state": "ELIGIBLE", "basis": f"SEEDED_SCREEN_INCLUDE:{f['stage']}", "pmid": f.get("pmid")}
    if f.get("stage") in ("SCREENED_VIA_OTHER_REPORT",) and f.get("via_decision") == "include":
        return {"state": "ELIGIBLE", "basis": "SCREEN_INCLUDE_VIA_OTHER_REPORT", "via": f.get("via")}
    if f.get("stage") == "SCREENED_OUT" or (rec is not None and rec.get("decision") != "include"):
        rule = f.get("rule_id") or (rec or {}).get("rule_id")
        if two_readers_eligible(readings):
            return {"state": "ELIGIBLE", "basis": "TWO_READERS_JUDGE_ELIGIBLE", "screen_rule": rule,
                    "readings": readings[:6]}
        return {"state": "NOT_ELIGIBLE", "rule_id": rule,
                "reason": (f.get("reason") or (rec or {}).get("reason") or "")[:160], "readings": readings[:6]}
    return {"state": "NOT_ASSESSED", "why": f.get("stage") or ("NO_RECORD_HELD" if not pmid else "NOT_IN_SCREEN"),
            "pmid": pmid}


def screen_record_for(records, ncts, pmids):
    """OUR screen's decision record for a TRIAL named by identity (a lane file's own comparator set, whose labels are not
    the k-gap table's): any screened report whose id is one of its PMIDs or whose trial family is its NCT. A trial any
    report of which our screen INCLUDES is included; else the first exclusion; None when the trial never entered."""
    ncts, pmids = {str(n) for n in ncts or [] if n}, {str(p) for p in pmids or [] if p}
    hits = [r for r in records if str(r.get("id")) in pmids or str(r.get("trial_family_id") or "") in ncts
            or str(r.get("trial_family_id") or "").replace("PMID:", "") in pmids]
    inc = [r for r in hits if r.get("decision") == "include"]
    return (inc or hits or [None])[0]


def identification_of(x, t, slug, in_search):
    """How the trial entered the candidate set: OUR_SEARCH (its report is in our own screened corpus or pool) or
    REVIEW_REFERENCE_LIST (listed in the comparator's included studies: source meta, location in its list, digest)."""
    import secondary_meta_build as smb
    if x.get("in_our_pool") or in_search:
        return {"route": "OUR_SEARCH"}
    return smb.reference_list_identification(slug, t["label"]) or {"route": "REVIEW_REFERENCE_LIST",
                                                                   "source_meta": t.get("comparator_pmid")}


def topic(slug, T):
    import secondary_meta_build as smb
    import k_gap_counterfactual as cfm
    sp = os.path.join(ROOT, "registry", "secondary_meta", f"{slug}.json")
    S = _j(sp) if os.path.exists(sp) else {"comparator_pmid": None, "rows": [], "metas": {}, "tally": {},
                                           "skipped": {}, "registry": None, "_missing": True}
    if S.get("_missing"):
        import secondary_meta_build as _smb
        S["comparator_pmid"] = _smb.comparator_pmid(slug)
    rev = _j(os.path.join(ROOT, "docs", "reviews", slug, "review.json"))
    comp = S["comparator_pmid"]
    ours = smb.our_trials(slug)
    # POOL BASIS: this harness's own build of the topic WITH every open primary source it holds (PMC / Unpaywall full
    # text, posted CT.gov results, member records) -- k_gap_counterfactual.build_with_held_sources. The served page
    # may lag it; the trials it pools that the served page does not are listed (served_pool_lags).
    core, src = cfm.build_with_held_sources(slug)
    prim = next((o for o in core["outcomes"] if o.get("primary")), {})
    row_by_id = {str(t.get("id")): t for t in prim.get("trials", [])}
    pooled_ids = {str(t.get("id")) for t in prim.get("trials", [])}
    absent_by_id = {str(a.get("id")): str(a.get("reason") or a.get("reason_code") or "")[:240]
                    for a in prim.get("declared_absent_trials", [])}
    absent_code = {str(a.get("id")): a.get("reason_code") or a.get("absent_kind")
                   for a in prim.get("declared_absent_trials", [])}
    rows = [_row(d) for d in S["rows"]]
    comparator_rows_source = None
    own_comp = ((S.get("metas") or {}).get(comp) or {})
    own_ok = own_comp.get("usable") and (own_comp.get("positive_control") or {}).get("reproduced")
    if not any(r.meta_pmid == comp for r in rows) or not own_ok:
        # no comparator rows of our own, or our own SINGLE-model read of the comparator failed its control: the
        # forest-reader lane's DUAL-model read of the comparator, where that lane ACCEPTED it, replaces it (Mahmood 3 Oct:
        # forest plots via the dual-model recorded reader). balanced-crystalloids: our read NOT_REPRODUCED; the lane's
        # dual read of the same comparator reproduces its pool (DL / PM / REML).
        lane_rows, comparator_rows_source = lane_comparator_rows(slug, comp, ours)
        if lane_rows and any((u.get("acceptance") or {}).get("state") == "ACCEPTED" for u in comparator_rows_source or []):
            rows = [r for r in rows if r.meta_pmid != comp] + lane_rows
            S = dict(S, metas={k: v for k, v in (S.get("metas") or {}).items() if k != comp})
        elif not any(r.meta_pmid == comp for r in rows):
            rows += lane_rows
    by_fam = {}
    for r in rows:
        by_fam.setdefault(r.family_id, []).append(r)
    # a DUPLICATE_UNIT is the same comparator trial listed in a second table (k_gap_table.mark_duplicate_units): never twice
    comp_rows = [t for t in T["trials"] if t["slug"] == slug and t.get("drug") != "OTHER_AGENT"
                 and t.get("status") != "DUPLICATE_UNIT"]
    resolve_by_comparator_citation(comp_rows, S.get("comparator_pmid") or _smb_comparator(slug))
    other_agent = [t["label"][:60] for t in T["trials"] if t["slug"] == slug and t.get("drug") == "OTHER_AGENT"]
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    spec_name = (cfg.get("primary_outcome") or {}).get("name") or ""
    kw_all = list((cfg.get("primary_outcome") or {}).get("keywords") or [])
    trials, routes, pairs, matched_ids = [], Counter(), [], set()
    # COMPARATOR ROWS BY THE COMPARATOR'S OWN LABELS: a comparator trial with no identity of ours (no PMID/NCT resolved)
    # has no family, so its row in the comparator's own figure could never attach (metformin, 3 Oct: 'Ben Ayed 2009',
    # 'Legro 2007', ... read and accepted, never joined). Every comparator row is ALSO joined to the comparator's trial
    # list by label / acronym / author-year (secondary_meta_build.family_of_factory, unique or nothing); used only where
    # the family route found no row, and never for two trials.
    import secondary_meta_build as _smb
    import k_gap_result_agreement as _ra
    _ents = [{"id": t["label"][:60], "label": t["label"][:60],
              "acronyms": sorted({v["acronym"] for v in (t.get("study") or {}).values() if (v or {}).get("acronym")}),
              "author_year": (_ra.first_author_year(t["pmids"][0]) if t.get("pmids")
                              else ref_author_year(t["label"], comparator_refs(comp)))} for t in comp_rows]
    _cfam = _smb.family_of_factory(_ents)
    # the comparator's OTHER-AGENT trials: a row joining one of them is accounted for in the outcome-set completeness
    _oth = [t for t in T["trials"] if t["slug"] == slug and t.get("drug") == "OTHER_AGENT"]
    _all = _smb.family_of_factory(_ents + [{"id": "__other__::" + t["label"][:60], "label": t["label"][:60],
                                            "acronyms": sorted({v["acronym"] for v in (t.get("study") or {}).values()
                                                                if (v or {}).get("acronym")}),
                                            "author_year": None} for t in _oth])
    accounted_other = sum(1 for r in rows if r.meta_pmid == comp and str(_all(r) or "").startswith("__other__::"))
    comp_by_label = {}
    for r in rows:
        if r.meta_pmid != comp:
            continue
        lab = _cfam(r)
        if lab:
            comp_by_label.setdefault(lab, []).append(r)
    comp_by_label = {k: v[0] for k, v in comp_by_label.items() if len(v) == 1}
    row_owner = {id(r): k for k, r in comp_by_label.items()}
    used_rows = set()
    for t in comp_rows:
        mine = next((o for o in ours if (o.get("nct") and o["nct"] in (t.get("ncts") or []))
                     or o["pmid"] in (t.get("pmids") or [])), None)
        fam = mine["id"] if mine else None
        in_pool = is_pooled(mine, pooled_ids)
        if in_pool and row_by_id.get(str(mine["id"])):
            # OUR value is the row the held-source POOL uses, never the bare build's (a stale baseline value could make
            # the same-trials comparison agree with numbers the pool no longer uses -- codex review 3 Oct)
            mine = dict(mine, primary=our_value_from_row(row_by_id[str(mine["id"])]) or mine.get("primary"))
        sec = by_fam.get(fam, []) if fam else []
        # the comparator's OWN printed row for this trial, whatever its admission state: agreement asks what the
        # comparator pooled for the trial, not whether we may use its row as data
        theirs = pick_comparator_row(sec, comp, t["label"][:60], row_owner, used_rows, comp_by_label.get(t["label"][:60]))
        if theirs is not None:
            used_rows.add(id(theirs))
        vrow = None                       # the verified non-pool row that enters the same-trials pair
        if in_pool:
            matched_ids.add(str(mine["id"]))
            route, basis = "PRIMARY", (mine.get("primary") or {}).get("source") or f"our pool {mine['id']}"
            if theirs and mine.get("primary"):
                pairs.append((as_row(mine["primary"], t["label"], theirs.measure), theirs))
        else:
            refusal = absent_by_id.get(str(mine["id"])) if mine else None
            # ANTI-CIRCULARITY: a row sourced FROM the comparator never gives a trial a counted route, however well it
            # is verified (ELIXA: the comparator's own 4-point row, verified against ELIXA's text, read as PRIMARY)
            comp_ids = {comp} | ({S.get("comparator_doi")} - {None})
            countable = sm.g1_countable(sec, comp_ids)
            best = sorted(countable, key=lambda r: {"PRIMARY": 0, "TWO_SOURCE": 1}.get(sm.route_of(r), 2))
            ss = None if best else secondary_single(sec, S.get("metas") or {}, comp_ids, slug, mine, t)
            if best:
                route = sm.route_of(best[0])
                basis = f"meta {best[0].meta_pmid} {best[0].state} {(best[0].verification or {}).get('route') or ''}".strip()
                vrow = best[0]
                if theirs is not None:
                    pairs.append((best[0], theirs))
            elif ss and ss.get("row") is not None:
                route, basis = "SECONDARY_SINGLE", ss["basis"]
                vrow = ss["row"]
                if theirs is not None:
                    pairs.append((ss["row"], theirs))
            elif any(r.state != sm.REFUSED for r in sec):
                route = "UNVERIFIED"
                basis = ("only the comparator's own row (never counts: anti-circularity)"
                         if all(r.meta_pmid == comp for r in sec if r.state != sm.REFUSED) else
                         "a non-comparator meta row, not admissible as SECONDARY_SINGLE: " + ((ss or {}).get("why") or "?"))
            else:
                route = "NO_ROW"
                basis = (t.get("gap_class") or "") + (
                    f" (secondary refused: {sorted({x for r in sec for x in r.reasons})[:3]})" if sec else "")
        routes[route] += 1
        trials.append({"label": t["label"][:60], "family": fam, "in_our_pool": in_pool, "route": route, "basis": basis,
                       "our_refusal": None if in_pool else (refusal or (t.get("gap_class") if not mine else None)),
                       "gap_class": t.get("gap_class"),
                       "absent_code": None if in_pool or not mine else absent_code.get(str(mine["id"])),
                       "comparator_row": ({k: getattr(theirs, k) for k in ("effect", "lower", "upper", "events_t", "n_t",
                                                                           "events_c", "n_c", "measure")}
                                          if theirs else None),
                       "comparator_row_findings": theirs.findings if theirs else [],
                       "comparator_row_provenance": ({"meta_pmid": theirs.meta_pmid, "location": theirs.location,
                                                      "digest": theirs.source_digest, "read": theirs.provenance,
                                                      "row_label": theirs.trial_label} if theirs else None),
                       "disagreement_side": ((theirs.verification or {}).get("which_side")
                                             if theirs and theirs.state == sm.MISMATCH else None),
                       "our_value": ({k: mine["primary"].get(k) for k in ("measure", "effect", "lower", "upper",
                                                                          "events_t", "n_t", "events_c", "n_c")}
                                     if in_pool and mine.get("primary") else row_value(vrow)),
                       "registry_binding": (registry_binding(t["ncts"][0], spec_name, kw_all,
                                                             estimand=(cfg.get("primary_outcome") or {}).get("estimand"),
                                                             population=(cfg.get("primary_outcome") or {}).get("population"))
                                            if not in_pool and (t.get("ncts") or []) else None),
                       "g1_countable": (in_pool and route == "PRIMARY") or bool(sm.g1_countable(sec, {comp}))
                                       or route == "SECONDARY_SINGLE",
                       "secondary_single": ({k: v for k, v in ss.items() if k != "row"} if (not in_pool and ss) else None),
                       # a trial matched through a VERIFIED non-pool row is compared on that row -- the same row its
                       # same-trials pair uses (empagliflozin-hfpef EMPEROR-Preserved, meta 35338608 PRIMARY_VERIFIED,
                       # read NOT_IN_OUR_POOL while its pair was in the comparison)
                       "agreement_with_comparator_row": agreement(mine and mine.get("primary"), theirs) if in_pool
                       else (agreement(row_value(vrow), theirs) if vrow is not None else "NOT_IN_OUR_POOL"), "comparator_row_state": theirs.state if theirs else None,
                       "comparator_row_reasons": list(theirs.reasons or []) if theirs else []})
    # comparator trials we hold NO record of: seed their held PubMed records through OUR build (in memory) once, so the
    # tracker says what our own screen/extraction does with each -- not just "identification gap"
    screened = {str(r["id"]): r for r in core["screening"]["records"]}
    rp = {id(t): report_pmid(t) for t in comp_rows}
    # a comparator reference that is a LETTER / COMMENT about a trial is that trial: PubMed's own CommentOn link (one
    # PMID, a report we hold) names it, never its title (sglt2-primary-prevention-hf 'Isreb (19)' = letter 31509682 on
    # CREDENCE 30990260). registry/comment_on.json: request + response sha256, fetched by scripts/g1_comment_on.py
    cop = os.path.join(ROOT, "registry", "comment_on.json")
    resolve_cited_letters(trials, comp_rows, rp, screened, _j(cop) if os.path.exists(cop) else {})
    for x, t in zip(trials, comp_rows):
        p = rp[id(t)]
        r = screened.get(p) if p else None
        if not x["in_our_pool"] and r is not None and r.get("decision") != "include":
            # ALREADY in our screen and excluded: the same funnel record a seeded one gets, so the audit gates it too
            x["seeded_funnel"] = {"stage": "SCREENED_OUT", "rule_id": r.get("rule_id"),
                                  "reason": (r.get("reason") or "")[:140], "pmid": p, "already_in_screen": True}
            x["our_refusal"] = f"IN SCREEN PMID {p}: SCREENED_OUT {r.get('rule_id')}: {(r.get('reason') or '')[:140]}"
    # EVERY comparator trial we do not pool, whatever its route: gating this on route NO_ROW skipped any trial that had
    # a comparator row joined (route UNVERIFIED) -- 45 trials in 12 topics never saw our screen, and when the label join
    # attached Radholm (9)'s row it lost its SCREENED_VIA_OTHER_REPORT match to the CANVAS pool row
    unseen = {rp[id(t)] for x, t in zip(trials, comp_rows) if needs_seed(x) and rp[id(t)] and rp[id(t)] not in screened}
    if unseen:
        mp = os.path.join(OUT, "member_records.json")
        held = _j(mp) if os.path.exists(mp) else {}
        recs = [held[p] for p in sorted(unseen) if p in held]
        fun = cfm.funnel(cfm.build(slug, extra_records=recs), [r["id"] for r in recs], recs) if recs else {}
        for x, t in zip(trials, comp_rows):
            p = rp[id(t)] if rp[id(t)] in fun else None
            if p and needs_seed(x):
                f = fun[p]
                x["seeded_funnel"] = dict(f, pmid=p)
                x["our_refusal"] = f"SEEDED PMID {p}: {f['stage']}" + (
                    f" {f.get('rule_id')}: {f.get('reason')}" if f.get("rule_id") else
                    f" {f.get('reason_code')}" if f.get("reason_code") else "")
            elif needs_seed(x) and rp[id(t)] in unseen:
                x["our_refusal"] = "NO_RECORD_HELD"
    # SAME TRIAL, OTHER REPORT: the comparator cites a secondary report (Radholm 2018, CANVAS heart-failure outcomes) whose
    # registered trial (the funnel's NCT link) we pool under its main report (Neal 2017, same NCT). The comparator trial
    # IS matched -- to that pool row -- once, and never to a pool row another comparator trial already matched.
    # The screen's own X-DEDUP verdict is the same link stated the other way round: 'companion/duplicate report of
    # TRANSFORM-3 (NCT02422186, already pooled)' -- esketamine Trial D is TRANSFORM-3's publication; we pool its
    # registry row NCT02422186.
    import re as _re
    nct_pool = {str(o.get("nct")): str(o.get("id")) for o in ours if o.get("nct") and str(o.get("id")) in pooled_ids}
    nct_pool.update({i: i for i in pooled_ids if str(i).startswith("NCT")})
    for x in trials:
        f = x.get("seeded_funnel") or {}
        if f.get("stage") == "SCREENED_OUT" and f.get("rule_id") == "X-DEDUP" and not f.get("via"):
            m = _re.search(r"\((NCT\d{8}), already pooled\)", f.get("reason") or "") or \
                _re.search(r"(NCT\d{8}), already pooled", x.get("our_refusal") or "")
            if m and nct_pool.get(m.group(1)):
                f = dict(f, stage="SCREENED_VIA_OTHER_REPORT", via=nct_pool[m.group(1)].replace("PMID ", ""),
                         via_decision="include", nct=m.group(1))
        via = (f.get("via") if str(f.get("via") or "").startswith("NCT") else f"PMID {f.get('via')}") if f.get("via") else None
        if (not x["in_our_pool"] and f.get("stage") == "SCREENED_VIA_OTHER_REPORT" and via and via not in pooled_ids
                and via in absent_code):
            # the report we include for this trial is itself declared absent for the outcome (pcsk9 GLAGOV: JAMA 2016,
            # 27846344, declared from its abstract; no full text held) -- that declaration, not the screen, is the blocker
            x["via_report_absent"] = {"id": via, "code": absent_code[via], "reason": absent_by_id.get(via),
                                      "full_text_held": full_text_held(via.replace("PMID ", ""))}
        if (x["in_our_pool"] or f.get("stage") != "SCREENED_VIA_OTHER_REPORT" or f.get("via_decision") != "include"
                or not via or via not in pooled_ids or via in matched_ids or not f.get("nct")):
            continue
        matched_ids.add(via)
        routes[x["route"]] -= 1
        routes["PRIMARY"] += 1
        x.update(in_our_pool=True, route="PRIMARY", family=via, g1_countable=True, our_refusal=None,
                 basis=f"same registered trial {f['nct']}: pooled under its report {via} (the comparator cites {f.get('pmid')})",
                 our_value=our_value_from_row(row_by_id[via]) if row_by_id.get(via) else None,
                 matched_via_other_report={"nct": f["nct"], "pool_row": via, "comparator_cites": f.get("pmid")})
        cr = x.get("comparator_row")
        if cr and x["our_value"]:
            theirs = sm.SecondaryRow(meta_pmid=comp, meta_doi="", location={}, source_digest="", provenance="COMPARATOR_ROW",
                                     trial_label=x["label"], measure=cr.get("measure") or "", outcome_definition="",
                                     **{k: cr.get(k) for k in ("effect", "lower", "upper", "events_t", "n_t", "events_c", "n_c")})
            x["agreement_with_comparator_row"] = agreement(x["our_value"], theirs)
            pairs.append((as_row(x["our_value"], x["label"], theirs.measure), theirs))
        else:
            x["agreement_with_comparator_row"] = "NOT_COMPARABLE:NO_COMPARATOR_ROW"
    for k in [k for k, n in routes.items() if n <= 0]:
        del routes[k]
    own_ids = {str(r.get("id")) for r in _j(os.path.join(ROOT, "cache", slug, "records.json")).get("records", [])} \
        if os.path.exists(os.path.join(ROOT, "cache", slug, "records.json")) else set()
    for x, t in zip(trials, comp_rows):
        p = rp[id(t)]
        x["identification"] = identification_of(x, t, slug, bool(p and p in own_ids))
        x["screen_eligibility"] = screen_eligibility(x, screened.get(p) if p else None, p,
                                                     two_reader_readings(slug, sorted(set(t.get("pmids") or []) | ({p} if p else set()))))
    for x in trials:
        x["scope_difference"] = None if x["in_our_pool"] else scope_difference(x, cfg, slug)
        x["blocker"] = None if (x["in_our_pool"] or x["scope_difference"]) else blocker_class(x, slug)
        if x["scope_difference"] and x.get("route") in ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE"):
            # a trial NAMED out of scope never carries a counted route, whichever meta's row was verified for it: ELIXA's
            # 4-point composite, verified from a non-comparator meta's dual-read row once the forest reader's rows entered
            # the registry, read as PRIMARY again (consolidation 2026-10-04; plant test_g1_tracker_plants)
            routes[x["route"]] -= 1
            routes["UNVERIFIED"] += 1
            x["basis"] = (f"named out of scope ({x['scope_difference'].get('kind')}): a verified value is held "
                          f"({x.get('basis')}) but never gives an out-of-scope trial a counted route")
            x["route"], x["g1_countable"] = "UNVERIFIED", False
        if x.get("in_our_pool") and str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE"):
            x["analysis_set_attribution"] = analysis_set_attribution(slug, cfg, x)
    for k in [k for k, n in routes.items() if n <= 0]:
        del routes[k]
    # a registration the comparator cites that does not exist in the snapshot cannot identify its trial: say so
    # (pcsk9 ODYSSEY JAPAN: cited NCT02017898, not in AACT 2026-08-30; registry/comparator_nct_check.json)
    ncp = os.path.join(ROOT, "registry", "comparator_nct_check.json")
    bad_nct = set((_j(ncp) if os.path.exists(ncp) else {}).get("not_in_snapshot") or [])
    nct_of = {t["label"][:60]: [n for n in (t.get("ncts") or []) if n in bad_nct] for t in comp_rows}
    for x in trials:
        if nct_of.get(x["label"]) and x.get("blocker") == "IDENTIFICATION":
            x["blocker"] = "IDENTIFICATION:COMPARATOR_NCT_NOT_IN_REGISTRY"
            x["comparator_cites_unknown_nct"] = nct_of[x["label"]]
    _rep0 = ((rev.get("comparator") or {}).get("reported") or [{}])[0]
    outcome_set_differences(trials, (S.get("metas") or {}).get(comp) or lane_comp_meta(comparator_rows_source), comp, rows,
                            compared=_rep0 or None, accounted_other=accounted_other)
    sweep_merge(slug, trials, routes, pairs)
    name_reference_seeds_outside_membership(slug, comp, trials, T)
    name_letter_units_by_comment_on(slug, cfg, trials, rev)
    acquired_merge(slug, trials, routes, pairs, comp)
    side_from_trial_text(trials, slug)
    named = [{"trial": x["label"], **x["scope_difference"]} for x in trials if x.get("scope_difference")]
    open_gaps = [x["label"] for x in trials if not is_matched(x) and not x.get("scope_difference")]
    blockers = Counter(x["blocker"] for x in trials if x.get("blocker") and not is_matched(x))
    # 'same trials' are trials BOTH sides hold AND that stay in our eligible set: a trial named out of protocol scope is
    # neither matched (is_matched) nor compared (Zarpelon [20] entered through a verified meta row before it was named)
    pairs_excluded = []
    keep_pairs = []
    for p in pairs:
        px = pair_trial(p, trials)
        if px is not None and px.get("scope_difference"):
            pairs_excluded.append(px.get("label"))
        else:
            keep_pairs.append(p)
    pairs = keep_pairs
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
    out = {"schema_version": SCHEMA_VERSION, "slug": slug, "comparator_pmid": comp,
            "N_comparator_trials": len(trials), "k_matched": sum(1 for x in trials if is_matched(x)),
            "k_in_our_pool": sum(1 for x in trials if x["in_our_pool"]),
            "N_eligible": len(trials) - len(named), "named_differences": named, "open_gaps": open_gaps,
            "k_matched_of_comparator_N": f"{sum(1 for x in trials if is_matched(x))} of {len(trials)}",
            "comparator_set": next(({"state": tp.get("comparator_set_state"), "sources_tried": tp.get("sources_tried")}
                                    for tp in T["topics"] if tp["slug"] == slug), None),
            "blockers": dict(blockers), "top_blocker": (blockers.most_common(1)[0][0] if blockers else None),
            "other_agent_units": other_agent,
            "comparator_findings": comparator_findings(trials, comp) + [
                {"finding": "COMPARATOR_CITES_NCT_NOT_IN_REGISTRY", "trial": x["label"], "comparator": comp,
                 "basis": f"{', '.join(x['comparator_cites_unknown_nct'])} is not in the AACT snapshot "
                          "(registry/comparator_nct_check.json)"} for x in trials if x.get("comparator_cites_unknown_nct")],
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if is_matched(x))),
            "same_trials": dict(same_trials_compare(pairs, method),
                                method_basis=("comparator positive control reproduced " + method) if pc.get("methods")
                                else "comparator positive control not reproduced: PM default",
                                excluded_named_scope_differences=pairs_excluded),
            "ours": {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")},
            "comparator": {k: rep.get(k) for k in ("outcome", "estimate", "ci_low", "ci_high", "scale")},
            "comparator_basis": comp_basis, "comparator_rows_source": comparator_rows_source,
            "ours_not_in_comparator": extra, "ours_not_in_comparator_detail": extra_detail,
            "secondary_tally": S["tally"], "secondary_skipped": S["skipped"], "registry": S.get("registry")}
    if ((out["same_trials"].get("verdict") or {}).get("verdict") or "").startswith(("DIFFERENT_CONCLUSION",
                                                                                     "SAME_CONCLUSION_DIFFERENT")):
        out["same_trials"]["attribution"] = verdict_attribution(pairs, method, trials)
    sk, sspan = comparator_stated_k(comp)
    out["comparator_stated_k"] = {"k": sk, "span": sspan}
    if sk is not None and sk > out["N_comparator_trials"]:
        # the comparator's own abstract states MORE trials than its enumerated list holds. Either our enumeration missed
        # a trial (dpp4: '6 trials'; CAROLINA is in its references, absent from ours) or the comparator's count is wrong
        # (iv-iron: 'six randomized controlled trials', and both of its own tables list five). Stated, never resolved here.
        out["comparator_findings"].append({"finding": "COMPARATOR_STATED_K_ABOVE_ENUMERATED_N", "trial": "(the comparator set)",
                                           "comparator": comp, "stated_k": sk, "enumerated_N": out["N_comparator_trials"],
                                           "span": sspan, "basis": "check the comparator's own trial table: a trial "
                                           "missing from our enumeration, or a wrong count in the comparator"})
    _abs = _j(os.path.join(OUT, "comparator_abstracts.json")) if os.path.exists(os.path.join(OUT, "comparator_abstracts.json")) else {}
    _ab = _abs.get(str(comp))
    wp = whole_pool_comparison(out, printed_k=printed_trial_count(_ab if isinstance(_ab, str) else json.dumps(_ab or "")))
    if wp:
        out["same_trials_per_trial"] = out["same_trials"]
        out["same_trials"] = wp
    served_ids = {str(t.get("id")) for o_ in rev.get("outcomes", []) if o_.get("primary") for t in o_.get("trials", [])}
    out["pool_basis"] = {"build": "k_gap_counterfactual.build_with_held_sources",
                         "held_records": len(src[0]), "held_fulltext": len(src[1]), "held_unpaywall": src[3],
                         "held_registry": len(src[2])}
    out["served_pool_lags"] = sorted(pooled_ids - served_ids)
    out["g1r_reproduction"] = g1r_reproduction((S.get("metas") or {}).get(comp) or {}, comp, rows)
    lane_acc = next((u for u in comparator_rows_source or [] if (u.get("acceptance") or {}).get("state") == "ACCEPTED"), None)
    if out["g1r_reproduction"].get("state") == "NO_PER_TRIAL_ROWS" and lane_acc:
        # the comparator's rows were read by the forest-reader lane's TWO models; that lane ACCEPTED the figure only
        # when its rows reproduce the figure's own printed pool (its acceptance.methods_reproducing): that IS the
        # comparator's self-reproduction, on the whole figure (not the subset joined to comparator trials)
        out["g1r_reproduction"] = {"state": "REPRODUCED", "rows": lane_acc.get("rows"),
                                   "methods": (lane_acc.get("acceptance") or {}).get("methods_reproducing"),
                                   "where": f"figure {lane_acc.get('figure')} (g1/forest-reader {str(lane_acc.get('commit'))[:9]}, dual-model)",
                                   "control_basis": f"FOREST_READER_ACCEPTANCE ({(lane_acc.get('acceptance') or {}).get('pooled_anchor')})",
                                   "pooled": lane_acc.get("pooled_agreed")}
    if out["g1r_reproduction"].get("state") == "NO_PER_TRIAL_ROWS":
        out["g1r_reproduction"] = g1r_from_trials(out)
    apply_confirm_bindings(out)
    apply_confirm_bindings(out, os.path.join(OUT, "g1_binding", "bindings.json"))
    apply_secondary_bindings(out, os.path.join(OUT, "g1_binding", f"secondary_{out.get('slug')}.json"))
    apply_coverage(out)
    cite_or_demote(out, slug)
    bad = scope_citation_violations(out)
    if bad:
        raise SystemExit(f"G1 TRACKER REFUSED {slug}: comparator trial(s) non-eligible without rule + span: {bad}")
    out["g1_status"] = g1_status(out)
    res = ((out.get("same_trials") or {}).get("attribution") or {}).get("resolution")
    if res:
        out["g1_status"]["result_disagreement"] = res          # beside RESULT_AGREES, never instead of it
    if (out.get("comparator") or {}).get("estimate") is None:
        ab = comparator_primary_absence(slug, cfg, comp)
        if ab:
            from harness import comparator_membership as cmb
            st = cmb.stated_trial_count((held_record(slug, comp) or {}).get("abstract") or "")
            out["g1_status"] = {"state": "COMPARATOR_NO_PRIMARY_RESULT", "criteria": {}, "unmet": ["COMPARATOR_PRIMARY_RESULT"],
                                "excluded_by_scope": out["g1_status"].get("excluded_by_scope"),
                                "comparator_stated_trials": (st or {}).get("k"), "comparator_trials_listed": len(trials),
                                **ab}
    return out


_EFFECT_SENT = re.compile(r"[^.]*\b(?:RR|OR|HR|MD|SMD|WMD|risk ratio|odds ratio|hazard ratio|mean difference)\b\s*"
                          r"[=:,]?\s*\(?-?\d[^.]*(?:\.\d[^.]*)*\.", re.I)


def comparator_primary_absence(slug, cfg, comp):
    """The comparator reports NO pooled result for the topic's primary outcome: no sentence of its abstract -- or of its
    held full text, only when that text is verified as the named article (k_gap.held_text_identity NAMED_ARTICLE) --
    that carries an effect estimate names any comparator-outcome term. Returns the evidence (what it DOES pool, as
    verbatim sentences), or None when it cannot be shown (then the topic stays NOT_YET: an extraction miss is not this).
    dpp4-mace-t2d: van den ... 34754403 pools MI, stroke, HF hospitalisation, CV death, revascularisation, unstable
    angina and arrhythmias -- never 3-point MACE."""
    terms = [t for co in cfg.get("comparator_outcomes") or [] for t in [co.get("name")] + list(co.get("keywords") or [])
             if t and t.lower() not in ("hazard ratio", "odds ratio", "risk ratio", "primary outcome", "primary endpoint")]
    if not terms:
        return None
    crec = held_record(slug, comp) or {}
    texts = [("abstract", crec.get("abstract") or "")]
    try:
        from kgap import k_gap
        body, ref = k_gap.held_text(slug)
        ident = k_gap.held_text_identity(crec.get("abstract") or "", body)
        if ident.get("state") == "NAMED_ARTICLE":
            texts.append((f"held full text ({ref})", body))
        else:
            return None                             # a held text that may not be the comparator cannot show an absence
    except Exception:
        return None
    effects = [(where, s) for where, t in texts
               for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", re.sub(r"\s+", " ", t)) if _EFFECT_SENT.search(s)]
    if not effects or not texts[0][1]:
        return None
    low = [t.lower() for t in terms]
    if any(any(t in s.lower() for t in low) for _, s in effects):
        return None
    return {"why": "the comparator pools no result for the topic's primary outcome; every effect it reports is for "
                   "another outcome", "terms_searched": terms,
            "comparator_pools": [{"where": w, "sentence": s[:300]} for w, s in effects[:12]]}


def _fmt(r):
    if not r or r.get("estimate") is None:
        return "not printed"
    lo, hi = r.get("ci_low"), r.get("ci_high")
    ci = f" ({lo:.2f} to {hi:.2f})" if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) else " (no CI)"
    return f"{r.get('scale') or ''} {r['estimate']:.2f}{ci}".strip()


def headline(out):
    """Both denominators, always side by side, and how many comparator trials left the eligible one."""
    k = sum(o["k_matched"] for o in out)
    N = sum(o["N_comparator_trials"] for o in out)
    E = sum(o.get("N_eligible", o["N_comparator_trials"]) for o in out)
    st = Counter((o.get("g1_status") or {}).get("state") for o in out)
    rt = Counter({"PRIMARY": 0, "TWO_SOURCE": 0, "SECONDARY_SINGLE": 0})      # always all three, zero included
    rt.update(route_group(x_["route"]) for o in out for x_ in o["trials"] if is_matched(x_))
    g1r = Counter(((o.get("g1r_reproduction") or {}).get("state") or "NOT_COMPUTED") for o in out)
    x = N - E
    cov = sum(o.get("k_covered", o["k_matched"]) for o in out)
    cs = sum(o.get("k_comparator_sourced", 0) for o in out)
    cc = sum(1 for o in out if o.get("coverage_complete"))
    return (f"**COVERAGE {cov} of {N} comparator trials ({100 * cov / N:.0f}%; {cs} comparator-sourced)** | "
            f"**INDEPENDENTLY CONFIRMED {k} of {N} ({100 * k / N:.0f}%)** = PRIMARY + TWO_SOURCE + SECONDARY_SINGLE | "
            f"COVERAGE_COMPLETE topics {cc} | matched {k} of {E} eligible | "
            f"{x} comparator trials excluded by named scope/estimand difference, each with rule ID + source span (listed "
            f"per topic below) | matched by route: " + ", ".join(f"{r} {rt[r]}" for r in ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE")) +
            " | G1-R (comparator's own rows reproduce its pool, NOT G1): " + ", ".join(f"{s} {n}" for s, n in sorted(g1r.items())) +
            " | topics: " + ", ".join(f"{s} {n}" for s, n in sorted(st.items())) +
            ". Every G1_MATCHED row shows its excluded-by-scope count of the comparator's N.") if N else "no comparator trials"


def table():
    out = [_j(os.path.join(G1_DIR, f)) for f in sorted(os.listdir(G1_DIR)) if f.endswith(".json") and ".tmp" not in f]
    missing = sorted(set(served_topics()) - {o["slug"] for o in out})
    if missing:
        raise SystemExit(f"G1 TRACKER REFUSED: served topic(s) with no tracker row: {missing}")
    bad = {o["slug"]: v for o in out for v in [scope_citation_violations(o)] if v}
    if bad:
        raise SystemExit(f"G1 TRACKER REFUSED: comparator trial(s) non-eligible without a cited rule + span: {bad}")
    focus = ["glp1-ra-mace-t2d", "semaglutide-obesity-weight", "noac-vs-warfarin-af-stroke", "tocilizumab-covid19-mortality"]
    out.sort(key=lambda o: (focus.index(o["slug"]) if o["slug"] in focus else len(focus), o["slug"]))
    md = ["# G1 tracker (derived: scripts/g1_tracker.py; one source file per topic in outputs/k_gap/g1/)", "",
          "G1 MATCHED = every eligible comparator trial matched AND every matched trial verified (PRIMARY / TWO_SOURCE, never "
          "comparator-only) AND the result agrees on the same trials AND every divergence is named (rule / gate / side cited, "
          "with the source span establishing it).",
          "", headline(out), "",
          "| topic | G1 status | COVERAGE / N (comparator-sourced) | coverage complete | INDEPENDENTLY CONFIRMED / N | matched / eligible | excluded by scope (of N) | named differences | open gaps | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator | top blocker | source |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        r, st = o["routes"], o["same_trials"]
        same = (f"{st['measure']} {_fmt(st['ours'])} vs {_fmt(st['theirs'])}, k={st['k']}, {st['method']}: "
                f"**{(st.get('verdict') or {}).get('verdict')}**" if st.get("state") == "POOLED" else st.get("state"))
        nd = o.get("named_differences") or []
        gs = o.get("g1_status") or {}
        src = o.get("lane_source")
        md.append(f"| {o['slug']} | **{gs.get('state')}**" + (f" (unmet: {', '.join(gs.get('unmet') or [])})"
                                                              if gs.get("unmet") else "") +
                  f" | {o.get('k_covered', o['k_matched'])} / {o['N_comparator_trials']} ({o.get('k_comparator_sourced', 0)}) | "
                  f"{'yes' if o.get('coverage_complete') else 'no'} | "
                  f"{o['k_matched']} / {o['N_comparator_trials']} | "
                  f"{o['k_matched']} / {o.get('N_eligible', o['N_comparator_trials'])} | "
                  f"{len(nd)} of {o['N_comparator_trials']} | "
                  f"{len(nd)}: " + ", ".join(f"{d['trial']} ({d['kind']})" for d in nd) + f" | {len(o.get('open_gaps') or [])} | "
                  f"{r.get('PRIMARY', 0)} | "
                  f"{r.get('TWO_SOURCE', 0)} | {r.get('UNVERIFIED', 0)} | {r.get('NO_ROW', 0)} | "
                  f"{o['per_trial_agreement']} | {same} | {_fmt(o['ours'])} k={o['ours'].get('k')} | {_fmt(o['comparator'])} | "
                  f"{o.get('top_blocker') or '-'} | " + (f"lane {src['branch']}@{src['commit'][:9]}" if src else "acq/k-gap") + " |")
    # the dual-model forest reader's verdict on the comparator's own figure (scripts/g1_forest_reader.py): why a
    # comparator row exists, or the typed reason it cannot (e.g. a one-stage IPD comparator prints no trial rows)
    frp = os.path.join(ROOT, "registry", "model_proposals", "g1_forest_reader.json")
    fr = _j(frp) if os.path.exists(frp) else {}
    for o in out:
        md += ["", f"## {o['slug']} (comparator PMID {o['comparator_pmid']})", ""]
        v, sk = (fr.get("results") or {}).get(o["slug"]), (fr.get("skipped") or {}).get(o["slug"])
        if v:
            a = v.get("acceptance") or {}
            md.append(f"- DUAL FOREST READER (codex + agy) {v['figure']['fig_id']}: **{v['state']}** -- "
                      + (f"{len(v.get('secondary_rows') or [])} comparator rows; printed pool reproduced by "
                         f"{a.get('methods_reproducing')}" if v["state"] == "ACCEPTED" else
                         f"{', '.join(v.get('problems') or [])}"))
        elif sk:
            md.append(f"- DUAL FOREST READER: not read -- {sk.get('why') if isinstance(sk, dict) else sk}"
                      + (f"; {(sk.get('open_access') or {}).get('state')}" if isinstance(sk, dict) and sk.get("open_access") else ""))
        for x in o["trials"]:
            md.append(f"- {x['label']}: **{x['route']}** - {x['basis']}; vs comparator row: "
                      f"{x['agreement_with_comparator_row']}"
                      + (f"; our refusal: {x['our_refusal']}" if x.get("our_refusal") else "")
                      + (f"; comparator row finding: {x['comparator_row_findings']}" if x.get("comparator_row_findings") else "")
                      + (f"; side: {x['disagreement_side']}" if x.get("disagreement_side") else ""))
        for d in o.get("named_differences") or []:
            if d["kind"] == "PROTOCOL_SCOPE_DIFFERENCE":
                md.append(f"- NAMED {d['kind']}: {d['trial']} -- rule {d['rule_id']} ({d['screen_reason']}); protocol "
                          f"rule {d['protocol_rule']}; SPAN [{d['span_source']}]: \"{d['span']['text']}\"; "
                          f"registered eligibility: {d['registered_eligibility']}")
            elif d["kind"] == "NOT_AN_INCLUDED_TRIAL":
                md.append(f"- NAMED {d['kind']}: {d['trial']} -- {d['gate']}. COMPARATOR SPAN [{d['comparator_span_source']}]: "
                          f"\"{d['comparator_span']['text']}\"; UNIT SPAN [{d['span_source']}]: \"{d['span']['text']}\"")
            elif d["kind"] == "NOT_IN_COMPARATOR_OUTCOME_ANALYSIS":
                md.append(f"- NAMED {d['kind']}: {d['trial']} -- rule {d['rule_id']} ({d['protocol_rule']}); "
                          f"SPAN [{d['span_source']}]: \"{d['span']['text']}\"")
            else:
                an = d.get("registry_analysis") or {}
                md.append(f"- NAMED {d['kind']}: {d['trial']} -- rule {d.get('rule_id')}; {d['gate']}: {d['reason']}. "
                          f"SPAN [{d.get('span_source')}]: \"{(d.get('span') or {}).get('text')}\". Registry ({d['snapshot']['id']}): "
                          f"'{d['registry_outcome']}', arms " + ", ".join(f"{a.get('title')} {a['count']}/{a['n']}"
                                                                         for a in d.get("registry_arms") or [])
                          + (f", {an.get('param_type')} {an.get('param_value')} ({an.get('ci_lower')}-{an.get('ci_upper')})"
                             if an else "") + f"; the comparator pooled it as {d.get('comparator_pooled_it_as')}")
        for f in o.get("comparator_findings") or []:
            md.append(f"- COMPARATOR FINDING {f['finding']}: {f.get('trial') or '(the comparator set)'} -- comparator row {f.get('comparator_row')}"
                      + (f" vs trial report {f['trial_report']}" if f.get("trial_report") else "")
                      + (f"; {f['detail']}" if f.get("detail") else "") + (f" ({f['basis']})" if f.get("basis") else ""))
        for e in o.get("ours_not_in_comparator_detail") or []:
            md.append(f"- pooled by us, not listed by the comparator: {e['id']} ({e['year']}; comparator "
                      f"{e['comparator_year']}): {e['why_not_in_comparator']}")
    with open(os.path.join(OUT, "G1_TRACKER.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")
    canon = canonical(out)
    tmp = os.path.join(OUT, f"G1_TRACKER.json.{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(canon, fh, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, os.path.join(OUT, "G1_TRACKER.json"))
    return md


CANONICAL_SCHEMA = "g1_tracker_canonical_v1"
TOPIC_KEYS = ("slug", "g1_status", "unmet", "k_matched", "N_comparator_trials", "N_eligible", "excluded_by_scope",
              "open_gaps", "matched_by_route", "named_differences", "same_trials_verdict", "readers_agree_on_verdict",
              "top_blocker", "blockers", "comparator_pmid", "source", "matched_by_route_group", "g1r_reproduction",
              "secondary_single", "k_independent", "k_comparator_sourced", "k_covered", "coverage_complete",
              "discrepancy_findings", "comparator_sourced")


def canonical(out):
    """THE machine-readable tracker (Mahmood 3 Oct: the markdown's column order changed; no consumer may parse by
    position). Keys, never positions; every topic carries exactly TOPIC_KEYS (pinned by tests/test_g1_interfaces.py);
    add keys by bumping CANONICAL_SCHEMA, never rename them."""
    topics = {}
    for o in out:
        gs = o.get("g1_status") or {}
        src = o.get("lane_source")
        topics[o["slug"]] = {
            "slug": o["slug"], "g1_status": gs.get("state"), "unmet": list(gs.get("unmet") or []),
            "k_matched": o["k_matched"], "N_comparator_trials": o["N_comparator_trials"],
            "N_eligible": o.get("N_eligible", o["N_comparator_trials"]),
            "excluded_by_scope": len(o.get("named_differences") or []),
            "open_gaps": list(o.get("open_gaps") or []),
            "matched_by_route": dict(Counter(x["route"] for x in o["trials"] if is_matched(x))),
            "named_differences": [{"trial": d.get("trial"), "kind": d.get("kind"), "rule_id": d.get("rule_id") or d.get("gate"),
                                   "span": (d.get("span") or {}).get("text"), "span_source": d.get("span_source"),
                                   "pmid": d.get("pmid")} for d in o.get("named_differences") or []],
            "same_trials_verdict": ((o.get("same_trials") or {}).get("verdict") or {}).get("verdict")
                                   or (o.get("same_trials") or {}).get("state"),
            "readers_agree_on_verdict": (o.get("same_trials") or {}).get("readers_agree_on_verdict"),
            "top_blocker": o.get("top_blocker"), "blockers": dict(o.get("blockers") or {}),
            "comparator_pmid": o.get("comparator_pmid"),
            "matched_by_route_group": dict(Counter(route_group(x["route"]) for x in o["trials"] if is_matched(x))),
            "g1r_reproduction": o.get("g1r_reproduction"),
            "k_independent": o.get("k_independent", o["k_matched"]),
            "k_comparator_sourced": o.get("k_comparator_sourced", 0),
            "k_covered": o.get("k_covered", o["k_matched"]),
            "coverage_complete": bool(o.get("coverage_complete")),
            "discrepancy_findings": o.get("discrepancy_findings") or [],
            "comparator_sourced": [{"trial": x["label"], **((x.get("comparator_sourced") or {}).get("value") or {}),
                                    "from": (x.get("comparator_sourced") or {}).get("provenance")}
                                   for x in o["trials"] if x.get("coverage") == "COMPARATOR_SOURCED"],
            "secondary_single": [{"trial": x["label"], **((x.get("secondary_single") or {}).get("provenance") or {})}
                                 for x in o["trials"] if is_matched(x) and route_group(x["route"]) == "SECONDARY_SINGLE"],
            "source": {"branch": src["branch"], "commit": src["commit"]} if src else {"branch": "acq/k-gap", "commit": None}}
    k = sum(t["k_matched"] for t in topics.values())
    N = sum(t["N_comparator_trials"] for t in topics.values())
    E = sum(t["N_eligible"] for t in topics.values())
    return {"schema": CANONICAL_SCHEMA, "topic_keys": list(TOPIC_KEYS),
            "totals": {"k_matched": k, "N_comparator_trials": N, "N_eligible": E, "excluded_by_scope": N - E,
                       "matched_by_route": dict(sum((Counter(t["matched_by_route"]) for t in topics.values()), Counter())),
                       "matched_by_route_group": dict(sum((Counter(t["matched_by_route_group"]) for t in topics.values()), Counter())),
                       "g1r_reproduction": dict(Counter(((t["g1r_reproduction"] or {}).get("state") or "NOT_COMPUTED")
                                                        for t in topics.values())),
                       "INDEPENDENTLY_CONFIRMED": sum(t["k_independent"] for t in topics.values()),
                       "COMPARATOR_SOURCED": sum(t["k_comparator_sourced"] for t in topics.values()),
                       "COVERAGE": sum(t["k_covered"] for t in topics.values()),
                       "coverage_complete_topics": sum(1 for t in topics.values() if t["coverage_complete"]),
                       "discrepancy_findings": sum(len(t["discrepancy_findings"]) for t in topics.values()),
                       "topics_by_status": dict(Counter(t["g1_status"] for t in topics.values()))},
            "topics": topics}


def main(argv):
    if argv and argv != ["--table"]:
        T = _j(os.path.join(OUT, "k_gap_table.json"))
        os.makedirs(G1_DIR, exist_ok=True)
        T = with_identity_chain(T)
        for s in [a for a in argv if not a.startswith("--")]:
            o = topic(s, T)
            # ATOMIC: a concurrent reader (another process building the table) must never see a truncated file
            p = os.path.join(G1_DIR, f"{s}.json")
            tmp = f"{p}.{os.getpid()}.tmp"
            with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(o, fh, indent=1, ensure_ascii=False)
            os.replace(tmp, p)
    if "--no-table" in argv:
        return
    print("\n".join(table()[:4 + len(os.listdir(G1_DIR))]))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
