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
    return (r.get("class"), r.get("subclass")) if r else (None, None)


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
        return {"kind": "PROTOCOL_SCOPE_DIFFERENCE", "rule_id": f["rule_id"], "screen_reason": f.get("reason"),
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
    return out


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


def whole_pool_comparison(o):
    """When EVERY comparator trial is matched and the comparator prints no per-trial rows (an IPD / network meta), the
    'same trials' ARE both whole pools: compare our pooled result with the comparator's printed one, labelled as such,
    with both methods recorded (they may differ: e.g. our PM+HKSJ vs an IPD model). Otherwise None."""
    st = o.get("same_trials") or {}
    ours, comp = o.get("ours") or {}, o.get("comparator") or {}
    if st.get("state") == "POOLED" or o["k_matched"] != o["N_comparator_trials"] or o["named_differences"]:
        return None
    if ours.get("k") != o["N_comparator_trials"] or None in (ours.get("estimate"), ours.get("ci_low"),
                                                               ours.get("ci_high"), comp.get("estimate"),
                                                               comp.get("ci_low"), comp.get("ci_high")):
        return None
    m = (ours.get("scale") or "").upper()
    if m != (comp.get("scale") or "").upper():
        return {"state": "WHOLE_POOL_MEASURE_DIFFERS", "ours": ours.get("scale"), "theirs": comp.get("scale")}
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
      DIVERGENCES_NAMED      every non-match is a named difference citing its rule/gate, and every per-trial
                             disagreement carries the side it falls on"""
    tr = o["trials"]
    if not o.get("N_comparator_trials", len(tr)):
        cs = o.get("comparator_set") or {}
        return {"state": "COMPARATOR_NOT_ENUMERATED", "criteria": {}, "unmet": ["COMPARATOR_TRIAL_LIST"],
                "why": f"the comparator's trial list could not be enumerated from open sources "
                       f"({cs.get('state')}; tried {cs.get('sources_tried')})"}
    v = ((o.get("same_trials") or {}).get("verdict") or {}).get("verdict")
    dis = [x for x in tr if str(x.get("agreement_with_comparator_row") or "").startswith("DISAGREE")]
    crit = {
        "ALL_ELIGIBLE_MATCHED": o["N_eligible"] > 0 and o["k_matched"] == o["N_eligible"] and not o["open_gaps"],
        "MATCHED_ARE_VERIFIED": all(x["route"] in ("PRIMARY", "TWO_SOURCE") for x in tr if x["in_our_pool"]),
        "RESULT_AGREES": v == "AGREE",
        "DIVERGENCES_NAMED": all((d.get("protocol_rule") or d.get("gate")) for d in o["named_differences"])
                             and all(x.get("disagreement_side") for x in dis),
    }
    return {"state": "G1_MATCHED" if all(crit.values()) else "NOT_YET", "criteria": crit,
            "unmet": [k for k, ok in crit.items() if not ok]}


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
        if in_pool and not mine.get("primary"):
            # a trial the held-source build admitted: our value is its pool row (effect + CI, or the 2x2)
            mine = dict(mine, primary=our_value_from_row(row_by_id.get(str(mine["id"])) or {}))
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
            countable = sm.g1_countable(sec, {comp} | ({S.get("comparator_doi")} - {None}))
            best = sorted(countable, key=lambda r: {"PRIMARY": 0, "TWO_SOURCE": 1}.get(sm.route_of(r), 2))
            if best:
                route = sm.route_of(best[0])
                basis = f"meta {best[0].meta_pmid} {best[0].state} {(best[0].verification or {}).get('route') or ''}".strip()
            elif any(r.state != sm.REFUSED for r in sec):
                route = "UNVERIFIED"
                basis = "only the comparator's own row (never counts: anti-circularity)"
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
                       "g1_countable": (in_pool and route == "PRIMARY") or bool(sm.g1_countable(sec, {comp})),
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
    for x in trials:
        x["scope_difference"] = None if x["in_our_pool"] else scope_difference(x, cfg, slug)
        x["blocker"] = None if (x["in_our_pool"] or x["scope_difference"]) else blocker_class(x, slug)
    named = [{"trial": x["label"], **x["scope_difference"]} for x in trials if x.get("scope_difference")]
    open_gaps = [x["label"] for x in trials if not x["in_our_pool"] and not x.get("scope_difference")]
    blockers = Counter(x["blocker"] for x in trials if x.get("blocker"))
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
            "N_comparator_trials": len(trials), "k_matched": sum(1 for x in trials if x["in_our_pool"]),
            "N_eligible": len(trials) - len(named), "named_differences": named, "open_gaps": open_gaps,
            "k_matched_of_comparator_N": f"{sum(1 for x in trials if x['in_our_pool'])} of {len(trials)}",
            "comparator_set": next(({"state": tp.get("comparator_set_state"), "sources_tried": tp.get("sources_tried")}
                                    for tp in T["topics"] if tp["slug"] == slug), None),
            "blockers": dict(blockers), "top_blocker": (blockers.most_common(1)[0][0] if blockers else None),
            "other_agent_units": other_agent,
            "comparator_findings": comparator_findings(trials, comp),
            "k_ours_total": res.get("k"), "routes": dict(routes), "trials": trials,
            "per_trial_agreement": dict(Counter(x["agreement_with_comparator_row"] for x in trials if x["in_our_pool"])),
            "same_trials": dict(same_trials_pool(pairs, method),
                                method_basis=("comparator positive control reproduced " + method) if pc.get("methods")
                                else "comparator positive control not reproduced: PM default"),
            "ours": {k: res.get(k) for k in ("k", "estimate", "ci_low", "ci_high", "scale")},
            "comparator": {k: rep.get(k) for k in ("outcome", "estimate", "ci_low", "ci_high", "scale")},
            "comparator_basis": comp_basis, "comparator_rows_source": comparator_rows_source,
            "ours_not_in_comparator": extra, "ours_not_in_comparator_detail": extra_detail,
            "secondary_tally": S["tally"], "secondary_skipped": S["skipped"], "registry": S.get("registry")}
    wp = whole_pool_comparison(out)
    if wp:
        out["same_trials_per_trial"] = out["same_trials"]
        out["same_trials"] = wp
    served_ids = {str(t.get("id")) for o_ in rev.get("outcomes", []) if o_.get("primary") for t in o_.get("trials", [])}
    out["pool_basis"] = {"build": "k_gap_counterfactual.build_with_held_sources",
                         "held_records": len(src[0]), "held_fulltext": len(src[1]), "held_unpaywall": src[3],
                         "held_registry": len(src[2])}
    out["served_pool_lags"] = sorted(pooled_ids - served_ids)
    out["g1_status"] = g1_status(out)
    return out


def _fmt(r):
    if not r or r.get("estimate") is None:
        return "not printed"
    lo, hi = r.get("ci_low"), r.get("ci_high")
    ci = f" ({lo:.2f} to {hi:.2f})" if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) else " (no CI)"
    return f"{r.get('scale') or ''} {r['estimate']:.2f}{ci}".strip()


def table():
    out = [_j(os.path.join(G1_DIR, f)) for f in sorted(os.listdir(G1_DIR)) if f.endswith(".json") and ".tmp" not in f]
    missing = sorted(set(served_topics()) - {o["slug"] for o in out})
    if missing:
        raise SystemExit(f"G1 TRACKER REFUSED: served topic(s) with no tracker row: {missing}")
    focus = ["glp1-ra-mace-t2d", "semaglutide-obesity-weight", "noac-vs-warfarin-af-stroke", "tocilizumab-covid19-mortality"]
    out.sort(key=lambda o: (focus.index(o["slug"]) if o["slug"] in focus else len(focus), o["slug"]))
    md = ["# G1 tracker (derived: scripts/g1_tracker.py; one source file per topic in outputs/k_gap/g1/)", "",
          "G1 MATCHED = every eligible comparator trial matched AND every matched trial verified (PRIMARY / TWO_SOURCE, never "
          "comparator-only) AND the result agrees on the same trials AND every divergence is named (rule / gate / side cited).",
          "",
          "| topic | G1 status | matched / eligible | matched / comparator N | named differences | open gaps | PRIMARY | TWO_SOURCE | UNVERIFIED | NO_ROW | per-trial vs comparator row | same trials (ours vs theirs) | ours | comparator | top blocker | source |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for o in out:
        r, st = o["routes"], o["same_trials"]
        same = (f"{st['measure']} {_fmt(st['ours'])} vs {_fmt(st['theirs'])}, k={st['k']}, {st['method']}: "
                f"**{(st.get('verdict') or {}).get('verdict')}**" if st.get("state") == "POOLED" else st.get("state"))
        nd = o.get("named_differences") or []
        gs = o.get("g1_status") or {}
        src = o.get("lane_source")
        md.append(f"| {o['slug']} | **{gs.get('state')}**" + (f" (unmet: {', '.join(gs.get('unmet') or [])})"
                                                              if gs.get("unmet") else "") +
                  f" | {o['k_matched']} / {o.get('N_eligible', o['N_comparator_trials'])} | "
                  f"{o['k_matched']} / {o['N_comparator_trials']} | "
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
