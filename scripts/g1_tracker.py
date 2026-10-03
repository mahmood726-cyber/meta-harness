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
                           events_c=primary.get("events_c"), n_c=primary.get("n_c"))


def agreement(ours, theirs):
    """Our pooled value vs the comparator's printed row for the same trial: AGREE / DISAGREE / NOT_COMPARABLE[:why]."""
    if not ours or not theirs:
        return "NOT_COMPARABLE:NO_COMPARATOR_ROW" if ours else "NOT_COMPARABLE"
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
    return {"basis": "single-trial swaps of the same-trials pools (same method, same verdict rule)",
            "drivers": drivers, "per_trial": out,
            "closed": bool(drivers) and all(r["row_agreement"] and (r["driver"] or str(r["row_agreement"]).startswith("AGREE"))
                                            for r in out)}


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


def binding_verdict(spec_name, keywords, title, n_groups, is_primary=False):
    """One registry outcome through the binding gates, in order:
      OUTCOME_NOT_NAMED  the title names no topic keyword (generic anchors like 'primary outcome' do not count): being
                         the trial's PRIMARY outcome is not identity with OUR outcome
      ESTIMAND           a different composite: extract.composite_component_mismatch on the title as a definition, or a
                         composite title for a declared SINGLE outcome ('Death or Mechanical Ventilation' is not mortality)
      ARMS               fewer than two result groups with people-unit counts"""
    from harness import extract
    t = (title or "").lower()
    named = [k for k in keywords if k and k.lower() not in extract.GENERIC_ANCHORS and k.lower() in t]
    if not named:
        return {"gate": "OUTCOME_NOT_NAMED", "verdict": "REFUSED",
                "reason": "registry title names none of the topic's outcome keywords" + (" (it is the trial's PRIMARY "
                                                                                       "outcome)" if is_primary else "")}
    mm = definition_gate(spec_name, title)
    if not mm and not extract.declared_is_composite(spec_name) and extract._names_composite(title):
        mm = f"declared single outcome '{spec_name}' but the registry outcome is a composite: '{title}'"
    if mm:
        return {"gate": "ESTIMAND", "verdict": "REFUSED", "reason": mm, "named_by": named}
    if n_groups < 2:
        return {"gate": "ARMS", "verdict": "REFUSED", "reason": "fewer than two result groups with people-unit counts",
                "named_by": named}
    return {"gate": None, "verdict": "BINDABLE", "reason": None, "named_by": named}


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
        c.update(binding_verdict(spec_name, keywords, t, len({g["group"] for g in groups}),
                                 is_primary=(o.get("type") or "").upper() == "PRIMARY"))
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


def is_matched(x):
    """A comparator trial is MATCHED when it is in our pool, or when the two-source sweep verified its typed tuple
    (route SWEEP_*: two sources agreeing -- a meta row + the trial's own text, + its posted results, or two independent
    metas; never the comparator; scripts/g1_two_source_sweep.py). A lane file that does not state pool membership
    (in_our_pool null: g1/tocilizumab) counts a trial by its own verified route (g1_countable, PRIMARY / TWO_SOURCE)."""
    if x.get("in_our_pool"):
        return True
    if x.get("scope_difference"):
        return False                      # named out of scope: never matched, whatever value is held
    if x.get("g1_countable") and x.get("route") in ("PRIMARY", "TWO_SOURCE", "SECONDARY_SINGLE"):
        return True                       # a verified typed tuple for the comparator's trial (Mahmood 3 Oct)
    return str(x.get("route") or "").startswith("SWEEP_")


ROUTE_GROUP = {"PRIMARY": "PRIMARY", "SWEEP_META+TRIAL_TEXT": "PRIMARY", "SWEEP_META+AACT": "PRIMARY",
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


def outcome_set_differences(trials, comp_meta, comp, rows):
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
    crow = [r for r in rows if r.meta_pmid == comp]
    joined = [x for x in trials if x.get("comparator_row")]
    if not crow or len(joined) != len(crow):
        return []
    where = (f"table {comp_meta.get('table')}" if comp_meta.get("provenance") == "TYPED_TABLE" else
             f"figure {comp_meta.get('figure')}{(' panel ' + comp_meta['panel']) if comp_meta.get('panel') else ''} "
             f"(recorded read {comp_meta.get('record_id')})")
    span = (f"comparator PMID {comp} {where}: rows {[r.trial_label for r in crow]}; positive control reproduced "
            f"({pc.get('methods')}) against its printed pooled result ({comp_meta.get('control_basis') or 'TYPED_TABLE'})")
    named = []
    for x in trials:
        if x.get("in_our_pool") or x.get("scope_difference") or x.get("comparator_row"):
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


def scope_difference(x, cfg, slug=None):
    """A comparator trial we do not pool, NAMED: PROTOCOL_SCOPE_DIFFERENCE (our registered screen excludes it, rule
    cited) or ESTIMAND_DIFFERENCE (its only available result is a different estimand, gate cited). None when the
    trial is an open gap (it must then stay visible as NO_ROW, never be dropped)."""
    import re as _re
    f = x.get("seeded_funnel") or {}
    if f.get("stage") == "SCREENED_OUT":
        if not f.get("rule_id"):
            return None                     # a screen-out with no rule cited is a blocker, never a named difference
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
    if f.get("stage") in ("NOT_IN_SCREEN", "INCLUDED_NOT_IN_PRIMARY", "SCREENED_VIA_OTHER_REPORT"):
        return f["stage"]
    if x.get("our_refusal") == "NO_RECORD_HELD":
        return "NO_RECORD_HELD"
    if x.get("absent_code"):
        return f"EXTRACTION:{x['absent_code']}"
    if x["family"] is None:
        return "IDENTITY_UNRESOLVED" if (x.get("gap_class") or "").startswith("UNRESOLVED") else (x.get("gap_class") or "UNKNOWN")
    return x.get("gap_class") or "UNKNOWN"


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
            out.append({"finding": f.get("finding"), "trial": x["label"], "comparator": comp,
                        "comparator_row": x.get("comparator_row"), "detail": f.get("printed_vs_arm_derived")})
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
        if not v or v.get("state") != "RESOLVED" or t.get("ncts") or t.get("pmids"):
            continue
        t["ncts"] = [v["nct"]] if v.get("nct") else []
        t["pmids"] = [v["pmid"]] if v.get("pmid") else []
        t["identity_basis"] = [f"IDENTITY_CHAIN:{v.get('basis')}"]
        t["status"] = "RESOLVED_BY_CHAIN"
        if str(v.get("scope") or "").startswith("OTHER_AGENT"):
            t["drug"] = "OTHER_AGENT"
    return T


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
        if is_matched(x) or x.get("scope_difference"):
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


def whole_pool_comparison(o):
    """When EVERY comparator trial is matched and the comparator prints no per-trial rows (an IPD / network meta), the
    'same trials' ARE both whole pools: compare our pooled result with the comparator's printed one, labelled as such,
    with both methods recorded (they may differ: e.g. our PM+HKSJ vs an IPD model). Otherwise None."""
    st = o.get("same_trials") or {}
    ours, comp = o.get("ours") or {}, o.get("comparator") or {}
    # a reference seed outside the comparator's OWN stated membership (NOT_AN_INCLUDED_TRIAL) is not one of its trials:
    # the comparator's pool is then exactly the matched set
    nd = o.get("named_differences") or []
    n_set = o["N_comparator_trials"] - len(nd)
    if any(d.get("kind") != "NOT_AN_INCLUDED_TRIAL" for d in nd):
        # with any other named difference, the comparator's pool is the matched set only when the comparator ITSELF
        # states that many trials (harness/comparator_membership.py; doac-vte: acq names Majeed 2013 X1, and van Es
        # states "6 phase 3 trials" == 6 matched)
        from harness import comparator_membership as cmb
        st = cmb.stated_trial_count((held_record(o.get("slug"), o.get("comparator_pmid")) or {}).get("abstract") or "")
        if not st or st["k"] != n_set:
            return None
    if st.get("state") == "POOLED" or o["k_matched"] != n_set:
        return None
    if ours.get("k") != n_set or None in (ours.get("estimate"), ours.get("ci_low"),
                                                               ours.get("ci_high"), comp.get("estimate"),
                                                               comp.get("ci_low"), comp.get("ci_high")):
        return None
    m = (ours.get("scale") or "").upper()
    if m != (comp.get("scale") or "").upper():
        return {"state": "WHOLE_POOL_MEASURE_DIFFERS", "ours": ours.get("scale"), "theirs": comp.get("scale"),
                "outcome_check": whole_pool_event_check(o)}
    o_ = {k: ours[k] for k in ("estimate", "ci_low", "ci_high")}
    t_ = {k: comp[k] for k in ("estimate", "ci_low", "ci_high")}
    return {"state": "POOLED", "basis": "ALL_TRIALS_SHARED_WHOLE_POOLS (comparator prints no per-trial rows)",
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
        "RESULT_AGREES": v == "AGREE" and (not readers_differ or (o.get("same_trials") or {}).get("readers_agree_on_verdict") is True),
        "DIVERGENCES_NAMED": all((d.get("protocol_rule") or d.get("gate")) and (d.get("span") or {}).get("text")
                                 for d in nd)
                             and all(x.get("disagreement_side") for x in dis),
    }
    return {"state": "G1_MATCHED" if all(crit.values()) else "NOT_YET", "criteria": crit,
            "unmet": [k for k, ok in crit.items() if not ok], "excluded_by_scope": excl}


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
    if not any(r.meta_pmid == comp for r in rows):
        lane_rows, comparator_rows_source = lane_comparator_rows(slug, comp, ours)
        rows += lane_rows
    by_fam = {}
    for r in rows:
        by_fam.setdefault(r.family_id, []).append(r)
    comp_rows = [t for t in T["trials"] if t["slug"] == slug and t.get("drug") != "OTHER_AGENT"]
    other_agent = [t["label"][:60] for t in T["trials"] if t["slug"] == slug and t.get("drug") == "OTHER_AGENT"]
    cfg = _j(os.path.join(ROOT, "topics", slug + ".json"))
    spec_name = (cfg.get("primary_outcome") or {}).get("name") or ""
    kw_all = list((cfg.get("primary_outcome") or {}).get("keywords") or [])
    trials, routes, pairs, matched_ids = [], Counter(), [], set()
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
        theirs = next((r for r in sec if r.meta_pmid == comp), None)
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
                if theirs is not None:
                    pairs.append((best[0], theirs))
            elif ss and ss.get("row") is not None:
                route, basis = "SECONDARY_SINGLE", ss["basis"]
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
                       "disagreement_side": ((theirs.verification or {}).get("which_side")
                                             if theirs and theirs.state == sm.MISMATCH else None),
                       "our_value": ({k: mine["primary"].get(k) for k in ("measure", "effect", "lower", "upper",
                                                                          "events_t", "n_t", "events_c", "n_c")}
                                     if in_pool and mine.get("primary") else None),
                       "registry_binding": (registry_binding(t["ncts"][0], spec_name, kw_all)
                                            if not in_pool and (t.get("ncts") or []) else None),
                       "g1_countable": (in_pool and route == "PRIMARY") or bool(sm.g1_countable(sec, {comp}))
                                       or route == "SECONDARY_SINGLE",
                       "secondary_single": ({k: v for k, v in ss.items() if k != "row"} if (not in_pool and ss) else None),
                       "agreement_with_comparator_row": agreement(mine and mine.get("primary"), theirs) if in_pool
                       else "NOT_IN_OUR_POOL", "comparator_row_state": theirs.state if theirs else None})
    # comparator trials we hold NO record of: seed their held PubMed records through OUR build (in memory) once, so the
    # tracker says what our own screen/extraction does with each -- not just "identification gap"
    screened = {str(r["id"]): r for r in core["screening"]["records"]}
    rp = {id(t): report_pmid(t) for t in comp_rows}
    for x, t in zip(trials, comp_rows):
        p = rp[id(t)]
        r = screened.get(p) if p else None
        if not x["in_our_pool"] and r is not None and r.get("decision") != "include":
            # ALREADY in our screen and excluded: the same funnel record a seeded one gets, so the audit gates it too
            x["seeded_funnel"] = {"stage": "SCREENED_OUT", "rule_id": r.get("rule_id"),
                                  "reason": (r.get("reason") or "")[:140], "pmid": p, "already_in_screen": True}
            x["our_refusal"] = f"IN SCREEN PMID {p}: SCREENED_OUT {r.get('rule_id')}: {(r.get('reason') or '')[:140]}"
    unseen = {rp[id(t)] for x, t in zip(trials, comp_rows) if x["route"] == "NO_ROW" and not x.get("seeded_funnel")
              and rp[id(t)] and rp[id(t)] not in screened}
    if unseen:
        mp = os.path.join(OUT, "member_records.json")
        held = _j(mp) if os.path.exists(mp) else {}
        recs = [held[p] for p in sorted(unseen) if p in held]
        fun = cfm.funnel(cfm.build(slug, extra_records=recs), [r["id"] for r in recs], recs) if recs else {}
        for x, t in zip(trials, comp_rows):
            p = rp[id(t)] if rp[id(t)] in fun else None
            if p and x["route"] == "NO_ROW" and not x.get("seeded_funnel"):
                f = fun[p]
                x["seeded_funnel"] = dict(f, pmid=p)
                x["our_refusal"] = f"SEEDED PMID {p}: {f['stage']}" + (
                    f" {f.get('rule_id')}: {f.get('reason')}" if f.get("rule_id") else
                    f" {f.get('reason_code')}" if f.get("reason_code") else "")
            elif x["route"] == "NO_ROW" and not x.get("seeded_funnel") and rp[id(t)] in unseen:
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
    for x in trials:
        x["scope_difference"] = None if x["in_our_pool"] else scope_difference(x, cfg, slug)
        x["blocker"] = None if (x["in_our_pool"] or x["scope_difference"]) else blocker_class(x, slug)
        if x.get("in_our_pool") and str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE"):
            x["analysis_set_attribution"] = analysis_set_attribution(slug, cfg, x)
    outcome_set_differences(trials, (S.get("metas") or {}).get(comp) or {}, comp, rows)
    sweep_merge(slug, trials, routes, pairs)
    name_reference_seeds_outside_membership(slug, comp, trials, T)
    name_letter_units_by_comment_on(slug, cfg, trials, rev)
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
            "comparator_findings": comparator_findings(trials, comp),
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if is_matched(x))),
            "same_trials": dict(same_trials_pool(pairs, method),
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
    wp = whole_pool_comparison(out)
    if wp:
        out["same_trials_per_trial"] = out["same_trials"]
        out["same_trials"] = wp
    served_ids = {str(t.get("id")) for o_ in rev.get("outcomes", []) if o_.get("primary") for t in o_.get("trials", [])}
    out["pool_basis"] = {"build": "k_gap_counterfactual.build_with_held_sources",
                         "held_records": len(src[0]), "held_fulltext": len(src[1]), "held_unpaywall": src[3],
                         "held_registry": len(src[2])}
    out["served_pool_lags"] = sorted(pooled_ids - served_ids)
    out["g1r_reproduction"] = g1r_reproduction((S.get("metas") or {}).get(comp) or {}, comp, rows)
    cite_or_demote(out, slug)
    bad = scope_citation_violations(out)
    if bad:
        raise SystemExit(f"G1 TRACKER REFUSED {slug}: comparator trial(s) non-eligible without rule + span: {bad}")
    out["g1_status"] = g1_status(out)
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
    return (f"**Matched {k} of {N} comparator trials ({100 * k / N:.0f}%)** | matched {k} of {E} eligible | "
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
          "| topic | G1 status | matched / comparator N | matched / eligible | excluded by scope (of N) | named differences | open gaps | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator | top blocker | source |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        r, st = o["routes"], o["same_trials"]
        same = (f"{st['measure']} {_fmt(st['ours'])} vs {_fmt(st['theirs'])}, k={st['k']}, {st['method']}: "
                f"**{(st.get('verdict') or {}).get('verdict')}**" if st.get("state") == "POOLED" else st.get("state"))
        nd = o.get("named_differences") or []
        gs = o.get("g1_status") or {}
        src = o.get("lane_source")
        md.append(f"| {o['slug']} | **{gs.get('state')}**" + (f" (unmet: {', '.join(gs.get('unmet') or [])})"
                                                              if gs.get("unmet") else "") +
                  f" | {o['k_matched']} / {o['N_comparator_trials']} | "
                  f"{o['k_matched']} / {o.get('N_eligible', o['N_comparator_trials'])} | "
                  f"{len(nd)} of {o['N_comparator_trials']} | "
                  f"{len(nd)}: " + ", ".join(f"{d['trial']} ({d['kind']})" for d in nd) + f" | {len(o.get('open_gaps') or [])} | "
                  f"{r.get('PRIMARY', 0)} | "
                  f"{r.get('TWO_SOURCE', 0)} | {r.get('UNVERIFIED', 0)} | {r.get('NO_ROW', 0)} | "
                  f"{o['per_trial_agreement']} | {same} | {_fmt(o['ours'])} k={o['ours'].get('k')} | {_fmt(o['comparator'])} | "
                  f"{o.get('top_blocker') or '-'} | " + (f"lane {src['branch']}@{src['commit'][:9]}" if src else "acq/k-gap") + " |")
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
            md.append(f"- COMPARATOR FINDING {f['finding']}: {f['trial']} -- comparator row {f.get('comparator_row')}"
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
              "secondary_single")


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
