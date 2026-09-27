"""Offline census of pinned served inputs against the current pure label rules.

Run from any directory: python evidence/fixtures/build_derived_label_fixture.py.
No review is regenerated, no network is used, and controls never enter the census.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PIN = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
sys.path.insert(0, str(ROOT))
from harness import composite_rule as cr, estmeasure as em, narrative_rules as nr, outcome_tiers as ot


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.PIPE).decode("utf-8")


def controls():
    """Explicit synthetic oracles; positive means the named capability fires."""
    policy = {"allow": ["RR", "HR"], "predeclared": True, "decided_by": "__control_author",
              "decided_on": "2000-01-01", "rationale": "synthetic control", "basis": "protocol"}
    own = {d: {"value": "synthetic", "source": "__control_source"} for d in ot.DIMENSIONS}
    copied = {d: {"value": "synthetic", "source": "outcome.name"} for d in ot.DIMENSIONS}
    good = {"id": "__control_trial", "compat_dimensions": own}
    bad = {"id": "__control_trial", "compat_dimensions": copied}
    spec = {"common_outcome_policy": {**policy, "analysis_set": ["synthetic"]}}
    outcome = {"name": "__control_outcome", "population": "synthetic", "timepoint": "synthetic"}
    core = "cardiovascular death, myocardial infarction, stroke"
    cases = []

    def add(rule, positive, actual, expected):
        cases.append({"name": f"__control_{rule}_{'positive' if positive else 'negative'}",
                      "rule": rule, "positive": positive, "actual": actual, "expected": expected})

    add("input_label", True, em.input_label({"ai": 1}, "OR"), "OR")
    add("input_label", False, em.input_label({}, "RR"), None)
    add("mixture_policy", True, em.mixture_policy({"measure_mixture_policy": policy}) is not None, True)
    add("mixture_policy", False, em.mixture_policy({"measure_mixture_policy": {**policy, "predeclared": False}}), None)
    add("mixed_label", True, em.mixed_label(["HR", "RR"], policy), "mixed ratio (HR+RR, approximation per protocol)")
    add("mixed_label", False, em.mixed_label(["HR", "RR"]), "mixed ratio (HR+RR)")
    add("majority_measure", True, em.majority_measure(["HR", "HR", "RR"]), "HR")
    add("majority_measure", False, em.majority_measure(["HR", "RR"]), None)
    add("pool_measure_decision", True, em.pool_measure_decision(["HR", "RR", "HR"], ["UNSTATED"] * 3, policy)["state"], "MIXED_BY_POLICY")
    add("pool_measure_decision", False, em.pool_measure_decision(["HR", "RR"], ["UNSTATED"] * 2, None)["code"], "POOL_MEASURE_MIXED")
    add("adjustment_of", True, em.adjustment_of({"effect": 1, "source": "adjusted hazard ratio"}), "ADJUSTED")
    add("adjustment_of", False, em.adjustment_of({"effect": 1, "source": "multiplicity-adjusted interval"}), "UNSTATED")
    add("adjustment_mixture", True, em.pool_measure_decision(["HR"] * 2, ["ADJUSTED", "UNADJUSTED"], None)["code"], "POOL_ADJUSTMENT_MIXED")
    add("adjustment_mixture", False, em.pool_measure_decision(["HR"] * 2, ["UNSTATED"] * 2, None)["state"], "DERIVED")
    for d in ot.DIMENSIONS:
        add("input_dimensions_" + d, True, ot.input_dimensions(good)[d]["derived"], True)
        add("input_dimensions_" + d, False, ot.input_dimensions(bad)[d]["derived"], False)
        add("derived_label_" + d, True, ot.derived_label(outcome, [ot.input_dimensions(good)])[d]["state"], "DERIVED")
        add("derived_label_" + d, False, ot.derived_label(outcome, [ot.input_dimensions(bad)])[d]["state"], "NOT_SHOWN")
    add("tiers", True, ot.tiers(outcome, [good], spec)["primary"]["state"], "POLICY_APPLIED")
    add("tiers", False, ot.tiers(outcome, [bad], spec)["primary"]["state"], "NO_INPUT_SATISFIES_POLICY")
    add("composite_rule", True, cr.verdict(core + ", coronary revascularization", {})["state"], "SEPARATE_ANALYSIS")
    add("composite_rule", False, cr.verdict(core, {})["state"], "PRIMARY")
    for positive, definition in [(True, core + ", coronary revascularization"), (False, core)]:
        cc = ot.composite_compatibility({"name": "major adverse cardiovascular events"},
                                      [{"id": "__control_trial", "endpoint_definition_span": definition}], {}, {}, [])
        add("composite_compatibility", positive, cc["admission_changes"], ["__control_trial"] if positive else [])
    add("preregistration", True, ot.preregistration({"name": "Bleeding", "kind": "harm"}, "- **Harms** - none preregistered")["state"], "NOT_PREREGISTERED")
    add("preregistration", False, ot.preregistration({"name": "Bleeding", "kind": "harm"}, "- **O (harms)** - Bleeding")["state"], "PREREGISTERED")
    add("population_literal", True, nr.population_literal("Of 10 enrollees, 9 received at least 1 dose")["population"], "mITT: received at least 1 dose (9 of 10 randomised)")
    add("population_literal", False, nr.population_literal("No analysis population stated."), None)
    add("strategy_label", True, nr.strategy_label("After initial parenteral therapy", "__control_drug")["strategy"], "parenteral lead-in then __control_drug")
    add("strategy_label", False, nr.strategy_label("No treatment sequence stated.", "__control_drug")["strategy"], "NOT_STATED_IN_HELD_TEXT")
    return cases


def build():
    git("cat-file", "-e", PIN + "^{commit}")  # Missing commit is an error, never a skipped census.
    tree = set(git("ls-tree", "-r", "--name-only", PIN).splitlines())
    slugs = sorted(p.split("/")[2] for p in tree if p.startswith("docs/reviews/") and p.endswith("/index.html"))
    sources = {}

    def held(path):
        text = git("show", f"{PIN}:{path}")
        sources[path] = {"origin": PIN, "sha256": hashlib.sha256(text.encode()).hexdigest()}
        return text

    refusals = json.loads(held("docs/refusals.json"))
    records, unevaluable = [], []

    def missing(name, rule, reason):
        unevaluable.append({"name": name, "rule": rule, "reason": reason})

    for slug in slugs:
        review = json.loads(held(f"docs/reviews/{slug}/review.json"))
        topic_path = f"topics/{slug}.json"
        topic_bytes = (ROOT / topic_path).read_bytes()
        sources[topic_path] = {"origin": "worktree", "sha256": hashlib.sha256(topic_bytes).hexdigest()}
        topic = json.loads(topic_bytes)
        specs = {s["name"]: s for s in [topic["primary_outcome"], *topic.get("secondary_outcomes", []), *topic.get("harm_outcomes", [])]}
        cache_path = next((p for p in (f"cache/{slug}/records.json", f"docs/cache/{slug}/records.json") if p in tree), None)
        cached = json.loads(held(cache_path))["records"] if cache_path else []
        abstracts = {str(r["id"]): r.get("abstract") or "" for r in cached}
        titles = {str(r["id"]): r.get("title") for r in cached}
        protocol_path = f"protocols/{slug}.md"
        protocol = held(protocol_path) if protocol_path in tree else None
        for index, outcome in enumerate(review.get("outcomes", [])):
            name = f"{slug} :: {outcome['name']}"
            kind = "PRIMARY" if outcome.get("primary") else "NON_PRIMARY"
            spec = specs.get(outcome["name"])
            if spec is None:
                raise ValueError(f"No worktree outcome spec: {name}")
            trials = deepcopy(outcome.get("trials") or [])
            target = ((outcome.get("estimand_decision") or {}).get("target_scale") or spec.get("estimand") or "RR").upper()
            count_measure = target if target in ("RR", "OR") else "RR"
            per_trial = []
            for trial in trials:
                pid = str(trial.get("id", "")).replace("PMID ", "")
                trial_name = f"{name} :: {trial.get('id') or trial.get('label')}"
                abstract = abstracts.get(pid, "")
                literal = nr.population_literal(abstract, trial)
                # Never trust a precomputed literal from the served output.
                trial.pop("analysis_population_literal", None)
                if literal:
                    trial["analysis_population_literal"] = literal
                if not abstract:
                    missing(trial_name, "population_literal", "no held abstract for this trial ID" if cache_path else "neither pinned cache path exists")
                label = em.input_label(trial, count_measure)
                if label is None:
                    missing(trial_name, "input_label", "admitted input has no identifiable measure")
                agents = sorted((topic.get("intervention_agents") or {}).keys(), key=len, reverse=True)
                drug = next((a for a in agents if re.search(rf"(?i)\b{re.escape(a)}\b", abstract)), None)
                per_trial.append({"id": trial.get("id"), "label": trial.get("label"), "held_title": titles.get(pid),
                                  "abstract_present": bool(abstract), "input_label": label,
                                  "adjustment": em.adjustment_of(trial), "population_literal": literal,
                                  "strategy_label": nr.strategy_label(abstract, drug) if drug else None,
                                  "strategy_not_evaluated_reason": None if drug else "no configured intervention agent matched in held abstract"})
            labels = [t["input_label"] for t in per_trial]
            decision = em.pool_measure_decision(labels, [t["adjustment"] for t in per_trial], em.mixture_policy(spec))
            decision.setdefault("sensitivity_restricted_to", None)
            tier = ot.tiers(outcome, trials, spec) if trials else None
            composite = ot.composite_compatibility(outcome, trials, spec, abstracts, refusals.get(slug) if outcome.get("primary") else None)
            if not trials:
                for rule in ("pool_measure_decision", "derived_label", "tiers"):
                    missing(name, rule, "no admitted trials; pipeline tiers loop skips this outcome")
            if composite is None:
                core = ot.core_for(spec, outcome)
                missing(name, "composite_compatibility", "no declared or MACE-type core (not applicable)" if core is None else "no evaluable multi-component definition")
            else:
                for row in composite["rows"]:
                    if row["state"] == "NO_DEFINITION":
                        missing(f"{name} :: {row['id']}", "composite_compatibility", "no usable component definition: " + row["definition_from"])
            if protocol is None:
                missing(name, "preregistration", "pinned protocol missing; rule uses empty text")
            prereg = ot.preregistration(outcome, protocol)
            # Apply the pipeline's composite-policy intersection, without computing an effect.
            if tier and composite and composite["policy_declared"] and tier["primary"]["state"] in ("POLICY_APPLIED", "NO_POLICY_DECLARED"):
                ok = {str(x["id"]) for x in composite["rows"] if x["served"] == "ADMITTED" and x["state"] == "PRIMARY"}
                base = tier["primary"]["trials"] if tier["primary"]["state"] == "POLICY_APPLIED" else [str(t.get("id") or t.get("label")) for t in trials]
                keep = [i for i in base if i in ok]
                tier["primary"].update(state="POLICY_APPLIED" if keep else "NO_INPUT_SATISFIES_POLICY", trials=keep, composite_policy=cr.policy(spec))
            served_tier = ("PRIMARY" if tier["primary"]["state"] == "POLICY_APPLIED" and prereg["state"] != "NOT_PREREGISTERED" else "EXPLORATORY") if tier else None
            records.append({"name": name, "slug": slug, "outcome_index": index, "outcome": outcome["name"],
                            "kind": kind, "outcome_kind": outcome.get("kind"), "trial_count": len(trials),
                            "served_result_present": bool((outcome.get("result") or {}).get("estimate") is not None),
                            "count_measure": count_measure, "trials": per_trial,
                            "pool_measure_decision": decision, "derived_label": tier["derived_label"] if tier else None,
                            "tiers": tier, "composite_compatibility": composite,
                            "preregistration": prereg, "served_tier": served_tier,
                            "preregistration_applied_by_pipeline": bool(trials)})
    totals, denominators = {}, {}

    def tally(key, items, predicate, denominator):
        totals[key] = {"fires": sum(bool(predicate(x)) for x in items), "of": len(items)}
        denominators[key] = denominator

    for kind in ("PRIMARY", "NON_PRIMARY"):
        items = [r for r in records if r["kind"] == kind]
        desc = f"all {kind} outcome records, including zero-trial and unevaluable outcomes"
        tally(kind + ".mixed_measures", items, lambda r: len({t["input_label"] for t in r["trials"] if t["input_label"]}) > 1, desc)
        tally(kind + ".measure_refused", items, lambda r: r["pool_measure_decision"]["state"] == "REFUSED", desc + "; empty inputs return UNIDENTIFIED")
        tally(kind + ".label_not_derived", items, lambda r: r["derived_label"] is not None and not r["derived_label"]["matches_inputs"], desc + "; empty inputs are unevaluable, not fires")
        for dimension in ot.DIMENSIONS:
            tally(kind + "." + dimension + "_not_derived", items, lambda r, d=dimension: r["derived_label"] is not None and r["derived_label"][d]["state"] != "DERIVED", desc)
        tally(kind + ".composite_changes", items, lambda r: r["composite_compatibility"] and r["composite_compatibility"]["admission_changes"], desc + "; fire = at least one admission changes")
        tally(kind + ".not_preregistered", items, lambda r: r["preregistration"]["state"] == "NOT_PREREGISTERED", desc + "; direct rule evaluated even where pipeline skips")
        trial_items = [t for r in items for t in r["trials"]]
        tally(kind + ".population_literal", trial_items, lambda t: t["population_literal"] is not None, f"all admitted trial-outcome occurrences in {kind}; repeated trials count per outcome; missing abstracts stay in N")
    comparison = []
    primary = [r for r in records if r["kind"] == "PRIMARY" and r["served_result_present"]]
    nonprimary = [r for r in records if r["kind"] == "NON_PRIMARY"]
    comp_rows = [(r, x) for r in records if r["kind"] == "PRIMARY" and r["composite_compatibility"] for x in r["composite_compatibility"]["rows"]]
    for rule, previous, candidates, affected, unit in [
        ("mixed_measures", {"fires": 4, "of": 27}, primary, [r["name"] for r in primary if len({t["input_label"] for t in r["trials"] if t["input_label"]}) > 1], "primary outcomes with a served result.estimate (historical measure census definition)"),
        ("label_not_derived", {"fires": 26, "of": 27}, primary, [r["name"] for r in primary if not r["derived_label"]["matches_inputs"]], "primary outcomes with a served result.estimate"),
        ("composite_changes", {"fires": 3, "of": 25}, comp_rows, [f"{r['name']} :: {x['id']}" for r, x in comp_rows if x["admission_changes"]], "all admitted and composite-refused rows returned by primary composite_compatibility, including NO_DEFINITION"),
        ("not_preregistered", {"fires": 19, "of": 65}, nonprimary, [r["name"] for r in nonprimary if r["preregistration"]["state"] == "NOT_PREREGISTERED"], "all non-primary outcomes, including zero-trial outcomes"),
    ]:
        measured = {"fires": len(affected), "of": len(candidates)}
        comparison.append({"rule": rule, "previous": previous, "measured": measured, "agrees": measured == previous,
                           "denominator": unit, "affected": affected,
                           "denominator_members": [f"{r['name']} :: {x['id']}" for r, x in candidates] if rule == "composite_changes" else [r["name"] for r in candidates],
                           "limitation": "Historical baseline is aggregate-only here; current numerator and denominator members are listed."})
    comparison[2]["evaluable_subset"] = {"fires": sum(x["admission_changes"] for _, x in comp_rows),
                                        "of": sum(x["state"] != "NO_DEFINITION" for _, x in comp_rows)}
    comparison[2]["unevaluable_members"] = [f"{r['name']} :: {x['id']}" for r, x in comp_rows if x["state"] == "NO_DEFINITION"]
    # User-supplied historic expectations only; identifiers are located by held source text/title, not invented.
    dpp = next(r for r in records if r["slug"] == "dpp4-mace-t2d" and r["kind"] == "PRIMARY")
    dpp_checks = []
    # PMID/name associations verified in the pinned held records (title and abstract).
    historical_populations = {
        "PMID 23992601": ("SAVOR", None),
        "PMID 30418475": ("CARMELINA", "mITT: received at least 1 dose (6979 of 6991 randomised)"),
        "PMID 28893244": ("OMNeON", "analysed 4192 of 4202 randomised (not all randomised)"),
    }
    for trial in dpp["trials"]:
        literal = trial["population_literal"]
        trial_name, expected = historical_populations[trial["id"]]
        dpp_checks.append({"name": f"{dpp['name']} :: {trial['id']}", "trial_name": trial_name,
                           "held_title": trial["held_title"], "actual": literal, "expected_population": expected,
                           "agrees": (literal or {}).get("population") == expected})
    return {"schema_version": 1, "pinned_commit": PIN, "served_reviews": slugs, "sources": sources,
            "records": records, "totals": totals, "denominators": denominators,
            "unevaluable": unevaluable, "comparisons": comparison,
            "dpp4_population_checks": dpp_checks, "controls": controls()}


def report(data):
    lines = ["# Derived label corpus fixture", "", f"Pinned served reviews, abstracts, protocols and refusals: `{PIN}`.",
             "Topics and pure rule implementations are read from this worktree. No pipeline rerun or network access.", "",
             "| Input | Static or dynamic |", "|---|---|",
             "| Commit and historical comparison counts | Static, task-supplied baselines, never used to calculate results |",
             "| Synthetic __control_ cases and expected values | Static test oracles; excluded from every corpus total |",
             "| Review membership and source data | Dynamic git reads at pinned commit; SHA-256 recorded |",
             "| Topic policies | Dynamic worktree reads; SHA-256 recorded |",
             "| Rule outputs and totals | Dynamic pure-function evaluation; no research effect estimates generated |", "",
             f"Coverage: {len(data['served_reviews'])} served reviews; {len(data['records'])} outcome records.",
             "PRIMARY is the served outcome's primary flag, not its newly derived tier. NON_PRIMARY retains the original efficacy/harm kind.",
             "Population literals are injected before tiers(). Null literals on present abstracts are evaluated negatives, not missing data.",
             "Preregistration is also directly evaluated for empty outcomes; the pipeline would skip those, recorded separately.",
             "Empty outcomes have a refused measure decision and null derived label/tiers, avoiding vacuous DERIVED labels.",
             "Sensitivity is the rule's restriction target (null if absent); this fixture does not compute pooled effects.", "",
             "| Rule | Fires | N | What N counts |", "|---|---:|---:|---|"]
    for rule, total in data["totals"].items():
        lines.append(f"| {rule} | {total['fires']} | {total['of']} | {data['denominators'][rule]} |")
    lines += ["", "## Historical comparisons", "", "Previous totals alone cannot identify which prior members changed. All current firing outcomes/rows and denominator members follow; no membership is inferred."]
    for c in data["comparisons"]:
        lines += ["", f"### {c['rule']}: {'AGREES' if c['agrees'] else 'DISAGREES'}",
                  f"Previous {c['previous']['fires']}/{c['previous']['of']}; measured {c['measured']['fires']}/{c['measured']['of']}.",
                  f"N: {c['denominator']}", "", "Current fires:", ""]
        lines += ["- " + x for x in c["affected"]] or ["- None"]
        lines += ["", "Current denominator members:", ""] + ["- " + x for x in c["denominator_members"]]
        if "evaluable_subset" in c:
            subset = c["evaluable_subset"]
            lines += ["", f"Explicit evaluable subset: {subset['fires']}/{subset['of']}; full denominator above retains these NO_DEFINITION rows:", ""]
            lines += ["- " + x for x in c["unevaluable_members"]]
    lines += ["", "## DPP-4 source-backed population checks", "",
              "Historical expectations: CARMELINA mITT 6979/6991; OMNeON analysed 4192/4202; SAVOR null. Actual held-source results:", ""]
    for c in data["dpp4_population_checks"]:
        lines.append(f"- {c['trial_name']}: {'AGREES' if c['agrees'] else 'DISAGREES'} — {c['name']} ({c['held_title']}): {json.dumps(c['actual'], ensure_ascii=False)}")
    lines += ["", "## Unevaluable or inapplicable items (retained in denominators)", "",
              "No declared composite core is inapplicable; no definition or no trials is unevaluable. These are not silently dropped.", ""]
    lines += [f"- {x['name']} — {x['rule']}: {x['reason']}" for x in data["unevaluable"]]
    lines += ["", "Controls: one positive and one negative per named rule/dimension, explicitly synthetic and excluded from totals.", "",
              "Regenerate: `python evidence/fixtures/build_derived_label_fixture.py`", "",
              "Verify only: `python -m pytest -q tests/test_derived_label_corpus_fixture.py -p no:cacheprovider`", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    data = build()
    here = Path(__file__).resolve().parent
    (here / "derived_label_corpus.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (here / "DERIVED_LABEL_FIXTURE.md").write_text(report(data), encoding="utf-8")
    print(json.dumps(data["totals"], indent=2))
