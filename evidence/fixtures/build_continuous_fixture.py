"""Offline census: pinned served/held bytes, current topic declarations and extractor.

Run from any directory with Python; no network, pipeline rebuild, or source mutation.
Synthetic controls are deliberately separate from the real corpus and its totals.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness import continuous_identity as ci  # noqa: E402
from harness.ctgov_results import extract_ctgov, _extract_ctgov_continuous  # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
FIELDS = ("mean1", "sd1", "nc1", "mean2", "sd2", "nc2", "effect", "ci_low", "ci_high", "scale")


class PinnedDataError(RuntimeError):
    pass


def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if p.returncode:
        raise PinnedDataError(f"git {' '.join(args)}: {p.stderr.decode('utf-8', errors='replace')}")
    return p.stdout


def pinned_json(path, manifest):
    raw = git("show", f"{PINNED}:{path}")
    manifest[path] = {"revision": PINNED, "sha256": hashlib.sha256(raw).hexdigest()}
    return json.loads(raw)


def key(value):
    value = str(value)
    nct = re.search(r"\bNCT\d{8}\b", value)
    return nct.group() if nct else value.removeprefix("PMID ")


def continuous(outcome):
    return any(outcome.get(k) in ("MD", "SMD") for k in ("estimand", "served_estimand")) or (
        outcome.get("result", {}).get("scale") in ("MD", "SMD")) or any(
        t.get("scale") in ("MD", "SMD") or t.get("mean1") is not None
        for t in outcome.get("trials", []))


def controls():
    def measure(three=False):
        titles = ["drug 10 mg", "drug 20 mg", "placebo"] if three else ["drug 10 mg", "placebo"]
        groups = [{"id": f"g{i}", "title": t} for i, t in enumerate(titles)]
        return {"title": "__control_ synthetic change", "paramType": "MEAN",
                "dispersionType": "Standard Deviation", "groups": groups,
                "denoms": [{"counts": [{"groupId": g["id"], "value": "20"} for g in groups]}],
                "classes": [{"categories": [{"measurements": [
                    {"groupId": g["id"], "value": str(i + 1), "spread": "2"}
                    for i, g in enumerate(groups)]}]}]}
    rule = {"eligible_arm_terms": ["10 mg", "20 mg"], "basis": "__control_ synthetic rule"}
    three = measure(True)
    se = dict(measure(), dispersionType="Standard Error")
    own_n = copy.deepcopy(measure())
    own_n["classes"][0]["denoms"] = [{"counts": [
        {"groupId": "g0", "value": "11"}, {"groupId": "g1", "value": "12"}]}]
    interval = {"level": 95, "sidedness": "two-sided", "low": -2, "high": 2}
    cases = {}
    for name, text in [("median_unbiased", "median-unbiased"), ("flexible_doses", "flexible doses")]:
        proc = ci.ci_procedure([text], interval)
        try:
            result = {"se": ci.se_from_ci(interval, proc), "refused": False}
        except ValueError as e:
            result = {"se": None, "refused": True, "reason": str(e)}
        cases[f"__control_{name}"] = {"input": text, "ci": interval, "procedure": proc, **result}
    cases["__control_se_dispersion"] = {"input": se, "result": _extract_ctgov_continuous(se, ["drug"], ["placebo"])}
    cases["__control_three_arms"] = {"input": three, "rule": rule,
        "without_rule": _extract_ctgov_continuous(three, ["drug"], ["placebo"]),
        "with_rule": _extract_ctgov_continuous(three, ["drug"], ["placebo"], rule),
        "partial_rule": _extract_ctgov_continuous(three, ["drug"], ["placebo"],
                                                 {"eligible_arm_terms": ["10 mg"]})}
    cases["__control_class_denominators"] = {"input": own_n, "typed": ci.typed_measure(own_n),
        "result": _extract_ctgov_continuous(own_n, ["drug"], ["placebo"])}
    return cases


def build_fixture():
    git("cat-file", "-e", f"{PINNED}^{{commit}}")
    paths = set(git("ls-tree", "-r", "--name-only", PINNED).decode().splitlines())
    review_paths = sorted(p for p in paths if re.fullmatch(r"docs/reviews/[^/]+/review.json", p)
                          and not p.split("/")[2].endswith("-comparator"))
    manifest, inventory, rows, outcomes = {}, [], [], []
    for path in review_paths:
        review = pinned_json(path, manifest)
        slug = review["slug"]
        inventory.append({"slug": slug, "outcomes": [
            {"index": i, "name": o["name"], "continuous": continuous(o),
             "served_rows": len(o.get("trials", [])), "absent_rows": len(o.get("declared_absent_trials", []))}
            for i, o in enumerate(review["outcomes"])]})
        if not any(continuous(o) for o in review["outcomes"]):
            continue
        held_path = f"cache/{slug}/records.json"
        held = pinned_json(held_path, manifest)
        vp = f"cache/{slug}/verified_arms.json"
        verified = pinned_json(vp, manifest) if vp in paths else {}
        if vp not in paths:
            manifest[vp] = {"revision": PINNED, "state": "NOT_PRESENT_IN_PINNED_TREE"}
        tp = f"topics/{slug}.json"
        raw = (ROOT / tp).read_bytes()
        manifest[tp] = {"revision": "working tree (current declarations)", "sha256": hashlib.sha256(raw).hexdigest()}
        topic = json.loads(raw)
        specs = [topic["primary_outcome"], *topic.get("secondary_outcomes", []), *topic.get("harm_outcomes", [])]
        records = held.get("records", []) + held.get("ctgov", [])
        for oi, o in enumerate(review["outcomes"]):
            if not continuous(o):
                continue
            matches = [s for s in specs if s["name"] == o["name"]]
            if len(matches) != 1:
                raise ValueError(f"Outcome spec must match uniquely: {slug}: {o['name']}")
            spec = matches[0]
            outcome_key = f"{slug}::{oi}"
            plan = ci.analysis_plan(spec)
            members = [("SERVED", t) for t in o.get("trials", [])] + [
                ("ABSENT", t) for t in o.get("declared_absent_trials", [])]
            included = {key(t["id"]) for t in review["screening"]["records"] if t["decision"] == "include"}
            member_ids = [key(t["id"]) for _, t in members]
            if len(set(member_ids)) != len(member_ids) or set(member_ids) != included:
                raise ValueError(f"Included membership not fully represented: {outcome_key}: {included ^ set(member_ids)}")
            outcomes.append({"key": outcome_key, "slug": slug, "name": o["name"], "index": oi,
                             "analysis_plan": plan, "served_result": o.get("result"),
                             "included_ids": sorted(included), "combine_rule": ci.combine_rule(spec)})
            for state, t in members:
                pid = key(t["id"])
                recs = [r for r in records if str(r.get("id")) == pid]
                ncts = {r["nct"].upper() for r in recs if r.get("nct")}
                if re.fullmatch(r"NCT\d{8}", pid):
                    ncts.add(pid)
                if len(ncts) > 1:
                    raise ValueError(f"Conflicting registry identities: {pid}: {ncts}")
                nct = next(iter(ncts), None)
                for field in ("trial_family_id", "family_id"):
                    if nct and re.fullmatch(r"NCT\d{8}", str(t.get(field, ""))) and t[field] != nct:
                        raise ValueError(f"Served/held identifier disagreement: {pid}")
                oms = held.get("ctgov_results", {}).get(nct, [])
                texts = [{"id": str(r["id"]), "abstract": r["abstract"]} for r in records
                         if r.get("abstract") and ((nct and str(r.get("nct") or r.get("id")).upper() == nct)
                                                   or (not nct and str(r.get("id")) == pid))]
                args = (oms, spec["keywords"], topic["intervention_terms"], topic["comparator_terms"])
                without = extract_ctgov(*args)
                with_rule = extract_ctgov(*args, combine_rule=ci.combine_rule(spec))
                # Pinned rows lack registry_title. Recover only through a unique title prefix AND raw mean/SD tuple.
                candidates = []
                if state == "SERVED":
                    for om in oms:
                        ex = _extract_ctgov_continuous(om, [x.lower() for x in topic["intervention_terms"]],
                                                      [x.lower() for x in topic["comparator_terms"]], ci.combine_rule(spec))
                        if ex and all(ex.get(k) == t.get(k) for k in ("mean1", "sd1", "mean2", "sd2")) and (
                            om.get("title") == t.get("registry_title") or om.get("title", "")[:70] in t.get("source", "")):
                            candidates.append(om)
                    selection = "unique served source title prefix + raw mean/SD tuple (n deliberately not used)"
                else:
                    chosen_title = (with_rule or without or {}).get("registry_title")
                    candidates = [om for om in oms if om.get("title") == chosen_title] if chosen_title else []
                    selection = "current extractor selected title (with topic rule, then without); not a pipeline admission"
                om = candidates[0] if len(candidates) == 1 else None
                direct_without = (_extract_ctgov_continuous(
                    om, [x.lower() for x in topic["intervention_terms"]],
                    [x.lower() for x in topic["comparator_terms"]]) if om else None)
                direct_with = (_extract_ctgov_continuous(
                    om, [x.lower() for x in topic["intervention_terms"]],
                    [x.lower() for x in topic["comparator_terms"]], ci.combine_rule(spec)) if om else None)
                selected_measures = {}
                for route, result in [("without_rule", without), ("with_rule", with_rule)]:
                    selected = [m for m in oms if result and m.get("title") == result.get("registry_title")]
                    selected_measures[route] = ci.typed_measure(selected[0]) if len(selected) == 1 else None
                reason = None if om else ("NO_REGISTRY_ID" if not nct else "NO_HELD_REGISTRY_RESULTS" if not oms
                                         else "NO_UNIQUE_SELECTED_CONTINUOUS_MEASURE")
                typed = ci.typed_measure(om) if om else None
                declaration = (spec.get("ci_procedure_declared") or {}).get(nct)
                mb = ci.model_based_row(om, [x["abstract"] for x in texts], declaration) if om else {"state": "NO_REGISTRY_MEASURE"}
                procedures = [{"analysis_index": i, "ci": a["ci"],
                               **ci.ci_procedure([x["abstract"] for x in texts], a["ci"], declaration)}
                              for i, a in enumerate((typed or {}).get("analyses", []))]
                va = verified.get(pid)
                corroborated = bool(va and with_rule and with_rule.get("multi_arm_combined") and va.get("override")
                                    and va.get("outcome") == spec["name"] and all(
                                        abs(with_rule[k] - va[k]) <= .01 for k in ("mean1", "sd1", "mean2", "sd2"))
                                    and all(with_rule[k] == va[k] for k in ("nc1", "nc2")))
                row = {"key": f"{outcome_key}::{t['id']}", "outcome_key": outcome_key, "slug": slug,
                       "id": t["id"], "nct": nct, "nct_basis": "held record.nct or explicit registry ID; checked against served family ID",
                       "served_state": state, "served_values": {k: t[k] for k in FIELDS if k in t},
                       "served_source": t.get("source"), "served_absence_reason": t.get("reason_code") or t.get("reason"),
                       "registry_measure_title": om.get("title") if om else None,
                       "registry_measure_selection": selection, "registry_measure_candidates": [m.get("title") for m in candidates],
                       "typed_measure": typed, "extractor_without_rule": without, "extractor_with_rule": with_rule,
                       "continuous_extractor_without_rule": direct_without, "continuous_extractor_with_rule": direct_with,
                       "wrapper_selected_measures": selected_measures,
                       "model_based_row": mb, "ci_procedures": procedures, "ci_declaration": declaration,
                       "held_abstracts": texts, "analysis_plan": plan, "verified_arms": va,
                       "hand_override_corroborated": corroborated, "unevaluable_reason": reason}
                row["properties"] = {
                    "registry_measure_evaluable": om is not None,
                    "wrapper_returns_any_without_rule": without is not None,
                    "wrapper_returns_any_with_rule": with_rule is not None,
                    "continuous_extracts_without_rule": bool(without and without.get("mean1") is not None),
                    "continuous_extracts_with_rule": bool(with_rule and with_rule.get("mean1") is not None),
                    "wrapper_noncontinuous_fallback": bool(without and without.get("mean1") is None),
                    "combine_rule_rescues": direct_without is None and direct_with is not None if om else None,
                    "class_n_differs": (any(a["n_observed"] != a["n_analysis_set"] for a in typed["arms"])
                                        if typed and typed["arms"] else None),
                    "non_sd_dispersion": (any(a["dispersion_kind"] != "SD" for a in typed["arms"])
                                          if typed and typed["arms"] else None),
                    "flexible_ci": (any(p["procedure"] == ci.FLEXIBLE for p in procedures) if procedures else None),
                    "model_based_admitted": mb["state"] == "ADMITTED" if om else None,
                    "hand_override_corroborated": corroborated,
                }
                rows.append(row)
    totals, denominators, unevaluable = {}, {}, {}

    def count(name, items, values, unit):
        totals[name] = {"fires": sum(v is True for v in values), "of": len(items)}
        denominators[name] = unit
        unevaluable[name] = [x["key"] for x, v in zip(items, values) if v is None]

    for prop in rows[0]["properties"]:
        count(prop, rows, [r["properties"][prop] for r in rows], "all included continuous trial-outcome items; unevaluable retained")
    served = [r for r in rows if r["served_state"] == "SERVED"]
    count("served_continuous", rows, [r["served_state"] == "SERVED" for r in rows], "all included continuous trial-outcome items")
    count("served_class_n_differs", served, [r["properties"]["class_n_differs"] for r in served], "served continuous rows only; unevaluable retained")
    count("served_effect_ci_path", served, [r["served_values"].get("effect") is not None for r in served], "served continuous rows only")
    esk = [r for r in rows if r["slug"] == "esketamine-trd-madrs"]
    count("esketamine_model_admitted", esk, [r["properties"]["model_based_admitted"] for r in esk], "all included esketamine continuous items, including served ABSENT")
    for state in ("DECLARED", "MISSING_DATA_ASSUMPTION_NOT_DECLARED", "PRIMARY_ANALYSIS_NOT_DECLARED"):
        count(f"analysis_plan_{state}", outcomes, [o["analysis_plan"]["state"] == state for o in outcomes], "continuous outcomes, not trials")
    before = sum(r["served_state"] == "SERVED" for r in esk)
    rescued = [r for r in esk if r["served_state"] == "ABSENT" and r["hand_override_corroborated"]]
    comparisons = [
        {"claim": "served continuous rows", "readme": 6, "observed": len(served)},
        {"claim": "served rows with class-level n mismatch", "readme": {"fires": 2, "of": 6}, "observed": totals["served_class_n_differs"]},
        {"claim": "TRANSFORM-1 k before -> after registry/override corroboration", "readme": [3, 4], "observed": [before, before + len(rescued)]},
        {"claim": "esketamine model-based admitted", "readme": {"fires": 2, "of": 4}, "observed": totals["esketamine_model_admitted"]},
        {"claim": "served continuous effect+CI path", "readme": {"fires": 0, "of": 6}, "observed": totals["served_effect_ci_path"]},
    ]
    for c in comparisons:
        c["agrees"] = c["readme"] == c["observed"]
    return {"schema_version": 1, "pinned_commit": PINNED, "review_count": len(inventory),
            "source_manifest": manifest, "review_inventory": inventory, "outcomes": outcomes, "rows": rows,
            "totals": totals, "denominators": denominators, "unevaluable": unevaluable,
            "readme_comparisons": comparisons,
            "wrapper_fallbacks": [{"key": r["key"], "without_rule_title": r["extractor_without_rule"]["registry_title"],
                                   "without_rule_type": r["extractor_without_rule"].get("registry_measure_type"),
                                   "continuous_measure_refused_without_rule": r["continuous_extractor_without_rule"] is None}
                                  for r in rows if r["properties"]["wrapper_noncontinuous_fallback"]],
            "controls": controls()}


def render_report(f):
    lines = ["# Continuous corpus fixture", "", f"Served reviews and held records are pinned to `{PINNED}`.",
             "Current working-tree topic declarations and harness functions are used; their behavior is frozen by fixture equality.",
             "Source hashes and the complete review/outcome inventory are in `continuous_corpus.json`.", "",
             "## Static versus dynamic disclosure", "", "| Input | Status |", "|---|---|",
             "| Commit, MD/SMD selection rule, README comparison claims | Static, explicit |",
             "| Synthetic `__control_` values | Invented test inputs only; excluded from every total |",
             "| Review membership, IDs, registry arms, abstracts, verified arms | Read from pinned git objects |",
             "| Topic combine rules, CI declarations, analysis plans | Read from current topic files; SHA-256 recorded |",
             "| Extractor, typed arms, model states, CI procedures, counts | Recomputed with current harness |", "",
             "## Coverage and interpretation", "",
             f"Scanned {f['review_count']} reviews, all outcomes. Selected {len(f['outcomes'])} continuous outcomes and {len(f['rows'])} included trial–outcome items.",
             "Membership is checked against each review's included screening records; ABSENT is outcome-level extraction status, not trial exclusion.",
             "Served title recovery requires a unique source-title prefix plus raw means/SDs; denominators are deliberately not part of that match.",
             "Absent rows use the title selected by the current extractor. No title is guessed when selection fails.",
             "Registry extraction success is not full pipeline admission. The k comparison checks the registry combination and held override corroboration, not a rebuild or release verdict.",
             "CI procedures are recorded per registry analysis, with held abstracts and declarations kept separate. No analysis means the CI property is unevaluable.",
             "The pipeline emits continuous_analysis only for declared plans with continuous trials; this census evaluates every selected outcome regardless of that display gate.", "",
             "## Totals", "", "`fires` counts true observations; `of` retains unevaluable items. Unknown is not a negative finding.", "",
             "| Property | fires | of (N) | Denominator | Unevaluable |", "|---|---:|---:|---|---:|"]
    for name, t in f["totals"].items():
        lines.append(f"| {name} | {t['fires']} | {t['of']} | {f['denominators'][name]} | {len(f['unevaluable'][name])} |")
    lines += ["", "## Unevaluable items", ""]
    for row in f["rows"]:
        props = [p for p, ids in f["unevaluable"].items() if row["key"] in ids]
        if props:
            lines.append(f"- `{row['key']}`: {row['unevaluable_reason'] or 'no registry analysis for CI procedure'}; properties: {', '.join(props)}.")
    lines += ["", "## README comparison", "", "| Claim | README | Observed | Agreement |", "|---|---|---|---|"]
    for c in f["readme_comparisons"]:
        lines.append(f"| {c['claim']} | {json.dumps(c['readme'])} | {json.dumps(c['observed'])} | {'yes' if c['agrees'] else 'DISAGREEMENT'} |")
    lines += ["", "### Extractor scope finding", "",
              "The README multi-arm refusal is correct for `_extract_ctgov_continuous`, but must not be generalized to the broad `extract_ctgov` call.",
              "The fixture records both APIs. Broad non-continuous fallbacks are excluded from continuous-extraction counts."]
    for fallback in f["wrapper_fallbacks"]:
        lines.append(f"- `{fallback['key']}`: without a rule the continuous measure is refused, but the wrapper returns {fallback['without_rule_type']}: {fallback['without_rule_title']}.")
    lines += ["", "No disagreements with the listed README counts." if all(c["agrees"] for c in f["readme_comparisons"]) else
              "Every disagreement is shown above; fixture values are not tuned to the README.",
              "This comparison does not validate README pooled-effect/CI estimates, binary-row claims, or historical builds.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    fixture = build_fixture()
    directory = Path(__file__).resolve().parent
    (directory / "continuous_corpus.json").write_text(json.dumps(fixture, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    (directory / "CONTINUOUS_FIXTURE.md").write_text(render_report(fixture), encoding="utf-8")
    print(json.dumps({"totals": fixture["totals"], "comparisons": fixture["readme_comparisons"]}, indent=2))
