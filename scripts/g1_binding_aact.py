"""OWN-TUPLE EFFECT_CI from the trial's OWN posted CT.gov results (AACT snapshot), for a lane target with no row (G1
binding lane). Deterministic; no model. The posted outcome is chosen by the TOPIC, never by the comparator's numbers:

  A1 OUTCOME   the outcome title names the topic outcome by a non-generic keyword (not 'primary outcome' / 'hazard ratio')
  A2 ESTIMAND  harness.extract.composite_component_mismatch(topic outcome, title + description) == '' -- the same gate the
               tracker's registry binding uses: a 3-point topic never takes a posted 4-point composite ('MACE Plus');
               A2b (stricter, this binder only): an extra component named anywhere in the title or description refuses
  A3 ANALYSIS  a posted analysis of that outcome whose parameter is the topic estimand, with a numeric value AND both CI
               bounds (a one-sided upper bound alone is refused: EFFECT_CI needs both)
  A4 POPULATION intention-to-treat: an outcome whose title/population says per-protocol / on-treatment is refused
  A5 UNIQUE    exactly one (outcome, analysis) survives; two or more -> AMBIGUOUS, refused and named
The span is the AACT fields verbatim (title | description | parameter value [lower, upper]) with the snapshot id; the
tracker's apply_confirm_bindings re-checks that effect and both bounds are verbatim in it.

ARMS_COMBINED (a CONTINUOUS topic, estimand MD): the posted per-arm mean / SD / N of ONE outcome chosen by the topic --
  C1 OUTCOME     the title names the topic outcome by a non-generic keyword
  C2 TIMEPOINT   the topic's declared day ('Day 28') is in the title
  C3 OBSERVED    a topic declaring an observed-case estimand refuses an imputed analysis (LOCF / '... Endpoint')
  C4 POPULATION  not per-protocol / on-treatment
  C5 ARMS        every posted group is a MEAN with a Standard Deviation and a count; exactly ONE control arm (placebo,
                 naming no intervention agent); every other arm names an intervention agent
  C6 UNIQUE      exactly one outcome survives
A trial with two or more intervention (dose) arms vs the one shared control is COMBINED, never picked: all intervention
arms are merged into one group by the Cochrane Handbook formula (6.5.2.10), so the shared control is counted once
(unit-of-analysis rule) and no dose is selected (the ME-13 multi-arm guard forbids a pick, not the combination).

    python scripts/g1_binding_aact.py   -> outputs/k_gap/g1_binding/bindings_aact.json
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
from harness import extract  # noqa: E402
from kgap import aact_adapter  # noqa: E402

OUT = os.path.join(ROOT, "outputs", "k_gap", "g1_binding")
GENERIC = {"primary outcome", "primary endpoint", "primary end point", "primary composite outcome", "hazard ratio",
           "secondary outcome", "secondary endpoint"}
EST = {"HR": r"hazard ratio", "RR": r"risk ratio|relative risk", "OR": r"odds ratio"}
EXTRA = re.compile(r"unstable angina|revasculari[sz]ation|hospitali[sz]ation for heart failure|heart failure hospitali[sz]ation", re.I)
NOT_ITT = re.compile(r"per[- ]protocol|on[- ]treatment|as[- ]treated", re.I)


def outcome_descriptions(ncts):
    """{outcome_id: description} for the NCTs, one pass over the snapshot's outcomes.txt."""
    want, out = set(ncts), {}
    with open(os.path.join(aact_adapter.snapshot_dir(), "outcomes.txt"), encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
            if r.get("nct_id") in want:
                out[r["id"]] = r.get("description") or ""
    return out


def candidates(reg, desc, topic_name, keywords, estimand):
    kws = [k.lower() for k in keywords if k and k.lower() not in GENERIC and len(k) >= 4]
    est = re.compile(EST.get(estimand.upper(), re.escape(estimand)), re.I)
    out, refused = [], []
    for oid, o in (reg.get("outcomes") or {}).items():
        title = o.get("title") or ""
        if not any(k in title.lower() for k in kws):
            continue
        why = extract.composite_component_mismatch(topic_name, f"{title} {desc.get(oid, '')}")
        if not why and re.search(r"(\d+)[\s-]?point|three-point", topic_name or "", re.I) and                 EXTRA.search(f"{title} {desc.get(oid, '')}"):
            # A2b (this binder only, stricter than the shared gate, which reads only 'composite'/'primary' clauses): an
            # extra composite component named ANYWHERE in the posted title or description refuses
            why = "A2b: posted outcome names an extra component: " + EXTRA.search(f"{title} {desc.get(oid, '')}").group(0)
        if why:
            refused.append({"outcome_id": oid, "title": title, "gate": "A2_ESTIMAND", "why": why[:160]})
            continue
        if NOT_ITT.search(title) or NOT_ITT.search(o.get("population") or ""):
            refused.append({"outcome_id": oid, "title": title, "gate": "A4_POPULATION", "why": "per-protocol / on-treatment"})
            continue
        for a in reg.get("analyses") or []:
            if a["outcome_id"] != oid or not est.search(a.get("param_type") or ""):
                continue
            if not (a.get("param_value") and a.get("ci_lower") and a.get("ci_upper")):
                refused.append({"outcome_id": oid, "title": title, "gate": "A3_ANALYSIS", "why": f"no two-sided CI ({a.get('param_value')}, lower={a.get('ci_lower')!r}, upper={a.get('ci_upper')!r})"})
                continue
            out.append({"outcome_id": oid, "title": title, "description": desc.get(oid, ""), "type": o.get("type"),
                        "analysis_id": a.get("analysis_id"), "param_type": a["param_type"], "effect": a["param_value"],
                        "lower": a["ci_lower"], "upper": a["ci_upper"]})
    return out, refused


def combine_arms(arms):
    """Cochrane Handbook 6.5.2.10: groups (n, mean, sd) merged into one: N = sum n; M = sum(n m)/N; SD by the
    pairwise formula, applied sequentially. Deterministic; the tracker recomputes it from the span's numbers."""
    n, m, sd = arms[0]
    for n2, m2, sd2 in arms[1:]:
        N = n + n2
        sd = math.sqrt(((n - 1) * sd ** 2 + (n2 - 1) * sd2 ** 2 + n * n2 / N * (m ** 2 + m2 ** 2 - 2 * m * m2)) / (N - 1))
        m = (n * m + n2 * m2) / N
        n = N
    return n, m, sd


CONTROL = re.compile(r"\bplacebo\b", re.I)
IMPUTED = re.compile(r"\bLOCF\b|last observation|\bendpoint\b", re.I)
# a POPULATION / analysis-set field that states imputation (codex review merge-08315be6e:g1#3): the title alone missed
# 'missing values imputed using last observation carried forward (LOCF)' written in the population field
IMPUTED_POP = re.compile(r"\bLOCF\b|last observation carried|imputed|imputation|multiple imputation", re.I)
# 'placebo for / to match / matching <agent>' names the drug the placebo MIMICS: it is the control (review g1#4)
PLACEBO_FOR = re.compile(r"\bplacebo\s+(?:for|to\s+match|matching|matched\s+to|of)\s+[\w\-]+(?:\s+[\w\-]+)?|"
                         r"\bmatching\s+placebo\s+(?:for|to)\s+[\w\-]+", re.I)


def arm_role(title, agents):
    ag = re.compile("|".join(re.escape(a) for a in agents), re.I) if agents else None
    rest = PLACEBO_FOR.sub(" ", title or "")          # the agent named only as what the placebo mimics is not an arm
    if CONTROL.search(title or "") and not (ag and ag.search(rest)):
        return "control"
    return "intervention" if ag and ag.search(rest) else None


def arm_candidates(meas, counts, titles, outcomes, topic, agents):
    """C1-C6 over one NCT's posted outcomes. meas: {outcome_id: [measurement rows]}, counts: {outcome_id: {group: n}}."""
    po = topic.get("primary_outcome") or {}
    kws = [k.lower() for k in po.get("keywords") or [] if k and k.lower() not in GENERIC and len(k) >= 4]
    day = re.search(r"\bday[- ]?(\d+)", po.get("timepoint") or "", re.I)
    observed = bool(re.search(r"observed[- ]case", f"{po.get('name')} {json.dumps(po.get('trial_annotations') or {})}", re.I))
    out, refused = [], []
    for oid, o in outcomes.items():
        title = o.get("title") or ""
        if not any(k in title.lower() for k in kws) or oid not in meas:
            continue
        why = None
        if day and not re.search(r"\bday\s*" + day.group(1) + r"\b", title, re.I):
            why = ("C2_TIMEPOINT", f"title does not name Day {day.group(1)}")
        elif observed and IMPUTED.search(title):
            why = ("C3_OBSERVED", f"imputed analysis ({IMPUTED.search(title).group(0)}) for an observed-case estimand")
        elif observed and IMPUTED_POP.search(o.get("population") or ""):
            why = ("C3_OBSERVED", f"imputed analysis stated in the population field "
                                  f"({IMPUTED_POP.search(o.get('population') or '').group(0)}) for an observed-case estimand")
        elif NOT_ITT.search(title) or NOT_ITT.search(o.get("population") or ""):
            why = ("C4_POPULATION", "per-protocol / on-treatment")
        arms = []
        if not why:
            # one measurement row per posted group, and every posted group measured (review g1#1, g1#2): a group posted
            # twice (category / classification rows: subgroups) or a group with a count but no measurement refuses the
            # outcome -- an arm is never counted twice, and none silently disappears from the combination
            gids = [r["result_group_id"] for r in meas[oid]]
            split = sorted({g for g in gids if gids.count(g) > 1} |
                           {r["result_group_id"] for r in meas[oid] if (r.get("category") or r.get("classification"))})
            unmeasured = sorted(set((counts.get(oid) or {})) - set(gids))
            if split:
                why = ("C5_ARMS", f"group(s) {split} posted as several category/classification rows (subgroups, not arms)")
            elif unmeasured:
                why = ("C5_ARMS", f"group(s) {unmeasured} posted with a count but no mean/SD: the arms cannot all be combined")
        if not why:
            for r in meas[oid]:
                g = r["result_group_id"]
                n = (counts.get(oid) or {}).get(g)
                if (r.get("param_type") or "").upper() != "MEAN" or r.get("dispersion_type") != "Standard Deviation" or not n:
                    why = ("C5_ARMS", f"group {g}: not MEAN+SD+count ({r.get('param_type')}, {r.get('dispersion_type')}, n={n})")
                    break
                t = titles.get(g) or ""
                role = arm_role(t, agents)
                if role is None:
                    why = ("C5_ARMS", f"group {g} '{t[:60]}' is neither the control nor an intervention arm")
                    break
                arms.append({"group": g, "code": r.get("ctgov_group_code"), "title": t, "role": role,
                             "mean": r["param_value"], "sd": r["dispersion_value"], "n": str(n)})
            n_ctl = sum(a["role"] == "control" for a in arms)
            if not why and (n_ctl != 1 or not any(a["role"] == "intervention" for a in arms)):
                why = ("C5_ARMS", f"{n_ctl} control arm(s) and {len(arms) - n_ctl} intervention arm(s); exactly one control "
                                  f"and at least one intervention arm are required")
        if why:
            refused.append({"outcome_id": oid, "title": title, "gate": why[0], "why": why[1]})
            continue
        out.append({"outcome_id": oid, "title": title, "arms": arms})
    return out, refused


def arms_values(arms):
    """The combined two-group tuple from the posted arms (strings, 4 dp): intervention arms merged, control as posted."""
    iv = [(int(a["n"]), float(a["mean"]), float(a["sd"])) for a in arms if a["role"] == "intervention"]
    c = next(a for a in arms if a["role"] == "control")
    n_t, m_t, sd_t = combine_arms(iv)
    return {"measure": "MD", "mean_t": f"{m_t:.4f}", "sd_t": f"{sd_t:.4f}", "n_t": n_t,
            "mean_c": c["mean"], "sd_c": c["sd"], "n_c": int(c["n"]), "k_intervention_arms": len(iv),
            "combination": "Cochrane Handbook 6.5.2.10" if len(iv) > 1 else None}


def arms_span(title, arms):
    return title + " || " + " || ".join(f"{a['code']} {a['title']} [{a['role']}]: MEAN {a['mean']} Standard Deviation "
                                         f"{a['sd']} N {a['n']}" for a in arms)


def _posted_arms(ncts):
    """{nct: (meas {oid: rows}, counts {oid: {group: n}})} from the snapshot's measurement/count tables, one pass each."""
    want, meas, counts = set(ncts), {}, {}
    d = aact_adapter.snapshot_dir()
    with open(os.path.join(d, "outcome_measurements.txt"), encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
            if r.get("nct_id") in want:
                meas.setdefault(r["nct_id"], {}).setdefault(r["outcome_id"], []).append(r)
    with open(os.path.join(d, "outcome_counts.txt"), encoding="utf-8", errors="replace", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
            if r.get("nct_id") in want and r.get("scope") == "Measure" and r.get("units") == "Participants":
                counts.setdefault(r["nct_id"], {}).setdefault(r["outcome_id"], {})[r["result_group_id"]] = r["count"]
    return {n: (meas.get(n, {}), counts.get(n, {})) for n in want}


def topic_agents(cfg):
    a = cfg.get("intervention_agents") or cfg.get("intervention_terms") or []
    return sorted({x for v in a.values() for x in v} if isinstance(a, dict) else set(a))


def main():
    targets = json.load(open(os.path.join(OUT, "targets.json"), encoding="utf-8"))
    tgt = [t for t in targets if t.get("ncts") and t.get("route") in ("NO_ROW", "UNVERIFIED")]
    aact_adapter.ensure(sorted({n for t in tgt for n in t["ncts"]}))
    desc = outcome_descriptions(sorted({n for t in tgt for n in t["ncts"]}))
    snap = aact_adapter.snapshot()
    bindings, refused, continuous = [], [], []
    for t in tgt:
        cfg = json.load(open(os.path.join(ROOT, "topics", t["slug"] + ".json"), encoding="utf-8"))
        po = cfg.get("primary_outcome") or {}
        est = (po.get("estimand") or "").upper()
        if est == "MD":
            continuous.append((t, cfg))
            continue
        if est not in EST:
            continue
        for n in t["ncts"]:
            reg = aact_adapter.registry_for(n)
            if not reg:
                continue
            ok, ref = candidates(reg, desc, po.get("name") or "", po.get("keywords") or [], est)
            if len(ok) != 1:
                refused.append({"slug": t["slug"], "label": t["label"], "nct": n,
                                "why": ("A5_AMBIGUOUS" if ok else "NO_ADMISSIBLE_POSTED_OUTCOME"),
                                "candidates": [(c["outcome_id"], c["title"][:80], c["effect"]) for c in ok], "refused": ref})
                continue
            c = ok[0]
            span = f"{c['title']} | {c['description']} | {c['param_type']} {c['effect']} [{c['lower']}, {c['upper']}]"
            bindings.append({"slug": t["slug"], "label": t["label"], "pmid": (t.get("pmids") or [None])[0], "own_tuple": True,
                             "tuple_kind": "EFFECT_CI", "source_kind": "AACT",
                             "source": f"AACT {snap.get('id')} {n} outcome {c['outcome_id']} analysis {c['analysis_id']}",
                             "values": {"measure": est, "effect": c["effect"], "lower": c["lower"], "upper": c["upper"]},
                             "span": span, "rules": "A1-A5 scripts/g1_binding_aact.py", "refused_alternatives": ref})
    posted = _posted_arms(sorted({n for t, _ in continuous for n in t["ncts"]})) if continuous else {}
    for t, cfg in continuous:
        for n in t["ncts"]:
            reg = aact_adapter.registry_for(n)
            if not reg:
                continue
            meas, counts = posted.get(n, ({}, {}))
            ok, ref = arm_candidates(meas, counts, reg.get("group_titles") or {}, reg.get("outcomes") or {}, cfg,
                                     topic_agents(cfg))
            if len(ok) != 1:
                refused.append({"slug": t["slug"], "label": t["label"], "nct": n,
                                "why": ("C6_AMBIGUOUS" if ok else "NO_ADMISSIBLE_POSTED_OUTCOME"),
                                "candidates": [(c["outcome_id"], c["title"][:80], None) for c in ok], "refused": ref})
                continue
            c = ok[0]
            bindings.append({"slug": t["slug"], "label": t["label"], "pmid": (t.get("pmids") or [None])[0], "own_tuple": True,
                             "tuple_kind": "ARMS_COMBINED", "source_kind": "AACT",
                             "source": f"AACT {snap.get('id')} {n} outcome {c['outcome_id']}",
                             "values": arms_values(c["arms"]), "arms": c["arms"], "span": arms_span(c["title"], c["arms"]),
                             "rules": "C1-C6 scripts/g1_binding_aact.py", "refused_alternatives": ref})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "bindings_aact.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"bindings": bindings, "not_bound": refused}, fh, indent=1, ensure_ascii=False)
    for b in bindings:
        print("BOUND", b["slug"][:14], b["label"], b["values"], "|", b["span"][:150])
    for r in refused:
        print("NOT  ", r["slug"][:14], r["label"], r["nct"], r["why"], r["candidates"][:2], [(x["gate"], x["why"][:60]) for x in r["refused"]][:3])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
