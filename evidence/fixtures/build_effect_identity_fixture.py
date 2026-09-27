"""Offline rule probes on every served trial row at PINNED (not a pipeline rebuild).

Run from any directory. Only the fixture JSON and its Markdown report are written.
Rules receive frozen served rows, pinned topic specs, and pinned held abstracts;
one probe never mutates the input to another probe. See the generated report.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import fields
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness import effect_identity as ei, estmeasure, extract, synth  # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
DEST = Path(__file__).resolve().parent
DENOMINATORS = {
    "ci_representation": "Reported-effect rows; fires if any parsed CI is one-sided or repeated.",
    "uncertainty_state": "Reported-effect rows; fires when uncertainty_state returns an unresolved state.",
    "se_permitted": "Reported-effect rows with at least one parsed CI; fires if any parsed CI is refused an SE (not permission granted).",
    "zero_cell_state": "Count-only rows with ai; fires on DOUBLE_ZERO or SINGLE_ZERO_CELL. Incomplete cells remain in N as unevaluable.",
    "DoubleZero": "Rows taking a binary-count or event/person-time Study.yi_vi path; fires only on the DoubleZero exception. Other refusals remain in N as unevaluable.",
    "polarity_check": "Reported-effect rows on death/mortality/survival outcomes; fires on EVENT_POLARITY_MISMATCH or NORMALISED.",
    "multi_arm_groups": "All served trial rows, grouped within each outcome; fires for each row belonging to a shared-control group (not per group).",
    "apply_multi_arm_rule": "All served trial rows, grouped within each outcome; fires for each row held for undeclared shared control; declared resolutions are separately typed.",
    "count_only_under_hr": "All rows on outcomes whose declared estimand names HR; fires on count-only input without an established HR.",
    "hr_route": "All reported HR rows, using the full served outcome pool and declared estimand; fires when a routing record is returned.",
    "reconstruct_from_counts": "Reported effects with RR/OR target and a different non-HR, nonempty scale (pipeline reconstruction guard); fires on RECONSTRUCTED.",
    "transform_provenance": "All reported-effect rows; fires on an exactly reproduced source-to-served transform.",
    "conflict_check": "Rows with a published point, both CI ends, and complete own/alternative counts; includes NOT_COMPARABLE, never silently drops them. Fires on SOURCE_EFFECT_CONFLICT.",
    "published_model": "All served trial rows (pipeline calls unconditionally); fires if a model is documented rather than NOT_STATED_IN_HELD_TEXT.",
    "rate_ratio_labelled_as_rr": "All served trial rows; fires when served RR quotes a matching effect typed RATE_RATIO or IRR by extract. Unlocated or ambiguous source effects remain in N as UNEVALUABLE.",
}


def git(*args, input=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=input,
                          capture_output=True, check=True).stdout


def pinned_inputs(ref=PINNED):
    """Read git objects in one batch, including cache fallback without checkout."""
    git("cat-file", "-e", f"{ref}^{{commit}}")  # mandatory; missing history is an error
    paths = set(git("ls-tree", "-r", "--name-only", ref).decode().splitlines())
    slugs = sorted(p.split("/")[2] for p in paths
                   if p.startswith("docs/reviews/") and p.count("/") == 3
                   and p.endswith("/index.html"))
    if not slugs:
        raise ValueError("No served index pages at pinned commit")
    selected, record_paths = [], {}
    for slug in slugs:
        selected.extend([f"docs/reviews/{slug}/review.json", f"topics/{slug}.json"])
        record_paths[slug] = next((p for p in (f"cache/{slug}/records.json",
                                  f"docs/cache/{slug}/records.json") if p in paths), None)
        if record_paths[slug]:
            selected.append(record_paths[slug])
    raw = git("cat-file", "--batch", input="".join(f"{ref}:{p}\n" for p in selected).encode())
    blobs, pos = {}, 0
    for path in selected:
        end = raw.index(b"\n", pos)
        header = raw[pos:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ValueError(f"Missing required pinned object: {ref}:{path}")
        size = int(header[2])
        blobs[path] = json.loads(raw[end + 1:end + 1 + size])
        pos = end + size + 2
    return slugs, blobs, record_paths


def result(state, fires=False, detail=None, applicable=True, reason=None):
    out = {"state": state, "fires": fires, "applicable": applicable}
    if detail is not None:
        out["detail"] = detail
    if reason:
        out["reason"] = reason
    return out


def na(reason):
    return result("NOT_APPLICABLE", applicable=False, reason=reason)


def unknown(reason, detail=None):
    return result("UNEVALUABLE", fires=None, detail=detail, reason=reason)


def rate_ratio_labelled_as_rr(row, abstract, abstract_reason=None):
    """Bind the served tuple to its quotation, then to a held abstract sentence.

    All label recognition and typing belongs to extract. Matching all three
    numeric fields avoids borrowing another endpoint's rate ratio. Conflicting
    matching source types are unknown, never resolved by choosing a positive.
    """
    quotes = [(key, row[key]) for key in ("source", "quotation", "source_span")
              if isinstance(row.get(key), str) and row[key].strip()]
    if str(row.get("scale") or "").upper() != "RR" and quotes:
        return result("NOT_SERVED_RR", detail={"source_field": quotes[0][0]})
    wanted = tuple(row.get(k) for k in ("effect", "ci_low", "ci_high"))
    if None in wanted:
        return unknown("no complete served effect/CI tuple to locate in source")
    for origin, text in [*quotes, ("held_abstract", abstract or "")]:
        found = []
        for sentence in extract._sentences(extract._norm(text)):
            for match in extract._EFFECT.finditer(sentence):
                effect = extract._effect_from_match(match, sentence)
                if effect and all(abs(a - b) <= 1e-6 for a, b in zip(effect[1:], wanted)):
                    found.append({"source_field": origin, "sentence": sentence,
                                  "matched_text": match.group(0), "source_scale": effect.scale,
                                  "canonical_scale": estmeasure._CANON[effect.scale]})
        if found:
            if len({hit["source_scale"] for hit in found}) != 1:
                return unknown("matching source tuple has conflicting effect types", found)
            fires = (str(row.get("scale") or "").upper() == "RR"
                     and found[0]["source_scale"] in ("RATE_RATIO", "IRR"))
            return result("RATE_RATIO_LABELLED_AS_RR" if fires else "NO_RATE_RATIO_MISLABEL", fires, found)
    return unknown("quoted effect could not be located with extract's effect regex and served tuple"
                   + (f"; {abstract_reason}" if abstract_reason else ""))


def evaluate(row, spec, pool, abstract, intervention, comparator, abstract_reason=None):
    """Independent probes: arguments/guards from pipeline's effect-identity block.

    No recovery extraction, upstream selection, or sequential row removal is replayed.
    Absence of text is recorded as unknown evidence, not evidence of rule absence.
    """
    t = deepcopy(row)
    reported = t.get("effect") is not None
    target = str(spec.get("estimand") or "").upper()
    source = t.get("source") or ""
    out = {}
    cis = ei.ci_representation(source) if reported else []
    for rule in ("ci_representation", "uncertainty_state", "se_permitted"):
        out[rule] = na("no reported effect")
    if reported:
        out["ci_representation"] = result("PARSED" if cis else "NO_PARSED_CI",
            any(c["sidedness"] != "two-sided" or c["repeated"] for c in cis), cis)
        us = ei.uncertainty_state(source)
        out["uncertainty_state"] = result(us["state"] if us else "NO_UNRESOLVED_CI", bool(us), us)
        permitted = [ei.se_permitted(c) for c in cis]
        out["se_permitted"] = (result("SE_REFUSED" if not all(permitted) else "SE_PERMITTED",
                                      not all(permitted), permitted) if cis else
                               na("ci_representation parsed no interval; no typed CI to pass"))
        if not source:
            for rule in ("ci_representation", "uncertainty_state"):
                out[rule] = unknown("reported row has no source quotation")
    count_only = not reported and t.get("ai") is not None
    cells = [t.get(k) for k in ("ai", "n1i", "ci", "n2i")]
    zs = synth.zero_cell_state(*cells) if count_only else None
    out["zero_cell_state"] = (unknown("incomplete binary counts") if None in cells else
        result(zs or "NO_ZERO_CELL", bool(zs))) if count_only else na("not a count-only binary row")
    out["DoubleZero"] = na("neither binary counts nor event/person-time input")
    if t.get("ai") is not None or t.get("e1i") is not None:
        # Pipeline Study construction, including design guard and measure dispatch.
        allowed = {f.name for f in fields(synth.Study)} - {"study_effect", "zero_event_method"}
        args = {k: v for k, v in t.items() if k in allowed}
        args["label"] = t.get("label") or str(t.get("id"))
        selector = (spec.get("selector_estimand") or target or "RR").upper()
        args["measure"] = ("IRR" if t.get("e1i") is not None else "MD" if t.get("mean1") is not None
                           else selector if selector in ("RR", "OR") else "RR")
        try:
            synth.Study(**args).yi_vi()
            out["DoubleZero"] = result("NO_DOUBLE_ZERO")
        except synth.DoubleZero as exc:
            out["DoubleZero"] = result("DOUBLE_ZERO", True, str(exc))
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            out["DoubleZero"] = unknown(f"Study.yi_vi refused before a DoubleZero verdict: {exc}")
    pc = ei.polarity_check(t, spec.get("name"), spec)
    out["polarity_check"] = (result(pc["state"], pc["state"] in ("EVENT_POLARITY_MISMATCH", "NORMALISED"), pc)
                             if pc else na("not a reported effect on a death/survival outcome"))
    if pc and pc["state"] == "NOT_STATED":
        out["polarity_check"] = unknown("event orientation not stated in row quotation", pc)
    # Preserve object membership for hr_route's identity exclusion and group lookup.
    groups = ei.multi_arm_groups(pool)
    group = next((g for g in groups if any(x is row for x in g)), None)
    resolved, held = ei.apply_multi_arm_rule(pool, spec)
    out["multi_arm_groups"] = result("SHARED_CONTROL" if group else "NO_SHARED_CONTROL", bool(group),
                                    [x.get("id") for x in group] if group else None)
    rule = str(spec.get("multi_arm_rule") or "").upper()
    held_group = bool(group and rule not in ("COMBINE_ARMS", "SPLIT_CONTROL"))
    out["apply_multi_arm_rule"] = result("MULTI_ARM_SHARED_CONTROL_UNDECLARED" if held_group else
        rule if group else "NO_SHARED_CONTROL", held_group,
        {"output_rows": len(resolved), "held": held} if group else None)
    co = ei.count_only_under_hr(t, spec.get("estimand"), spec)
    out["count_only_under_hr"] = (result(co["state"] if co else "NO_COUNT_ONLY_INPUT", bool(co), co)
        if "HR" in target.replace("/", " ").split() else na("outcome target does not name HR"))
    hr = ei.hr_route(row, spec.get("estimand"), pool)
    out["hr_route"] = (result(hr["route"] if hr else "NO_ROUTING_REQUIRED", bool(hr), hr)
        if reported and str(t.get("scale") or "").upper() == "HR" else na("not a published HR"))
    reconstruct = reported and target in ("RR", "OR") and str(t.get("scale") or "").upper() not in (target, "HR", "")
    out["reconstruct_from_counts"] = na("pipeline incompatible-measure reconstruction guard is false")
    if reconstruct:
        rc = ei.reconstruct_from_counts(t, abstract, intervention, comparator, target)
        out["reconstruct_from_counts"] = (unknown(abstract_reason, rc) if abstract_reason else
            result(rc["state"], rc["state"] == "RECONSTRUCTED", rc))
    tp = ei.transform_provenance(t, abstract)
    out["transform_provenance"] = (unknown(abstract_reason) if abstract_reason and not tp else
        result(tp["reported_measure"] if tp else "NO_TRANSFORM", bool(tp), tp)) if reported else na("no reported effect")
    pm = ei.published_model(t, abstract)
    documented = pm["model"] != "NOT_STATED_IN_HELD_TEXT"
    out["published_model"] = (unknown(abstract_reason, pm) if abstract_reason and not documented else
                              result(pm["model"], documented, pm))
    cc = ei.conflict_check(t, ei.model_documented(t, abstract))
    out["conflict_check"] = (result(cc["state"], cc["state"] == "SOURCE_EFFECT_CONFLICT", cc)
        if cc else na("no complete published tuple plus complete own/alternative counts"))
    out["rate_ratio_labelled_as_rr"] = rate_ratio_labelled_as_rr(t, abstract, abstract_reason)
    return out


def controls():
    """Hand-built synthetic inputs, explicitly not research observations."""
    pub = {"effect": 0.6, "ci_low": 0.4, "ci_high": 0.9, "scale": "RR", "source": "risk ratio 0.6; 95% CI 0.4 to 0.9"}
    counts = {"ai": 10, "n1i": 100, "ci": 20, "n2i": 100}
    base_spec = {"name": "Mortality", "estimand": "RR"}
    cases = []
    for rule in DENOMINATORS:
        for positive in (True, False):
            row, spec, ab, peers = deepcopy(pub), dict(base_spec), "No estimation model stated.", []
            if rule in ("ci_representation", "uncertainty_state", "se_permitted"):
                if positive:
                    row["source"] = "hazard ratio, 0.96; upper boundary of the one-sided repeated confidence interval, 1.16"
            elif rule in ("zero_cell_state", "DoubleZero"):
                row = dict(counts, ai=0 if positive else 10, ci=0 if positive else 20)
            elif rule == "polarity_check":
                row["source"] = "odds of improvement" if positive else "deaths"
            elif rule in ("multi_arm_groups", "apply_multi_arm_rule"):
                row = dict(counts, trial_family_id="__control_family")
                if positive:
                    peers = [dict(counts, id="__control_peer", trial_family_id="__control_family", ai=15)]
            elif rule == "count_only_under_hr":
                spec["estimand"] = "HR"
                row = dict(counts) if positive else dict(pub, scale="HR")
            elif rule == "hr_route":
                row["scale"] = "HR"
                peers = [dict(counts, id="__control_peer")]
                if not positive:
                    spec["estimand"] = "HR"
            elif rule == "reconstruct_from_counts":
                row.update(scale="OR", source="Drug (10 [10%] vs 20 [20%])")
                ab = "Drug group (n=100) and placebo group (n=100)."
                if not positive:
                    row["source"] = "Drug (11 [10%] vs 20 [20%])"
            elif rule == "transform_provenance":
                row.update(effect=0.44, ci_low=0.27, ci_high=0.73,
                           source="relative risk reduction, 0.56 [CI, 0.27 to 0.73]" if positive else "risk ratio 0.44; 95% CI 0.27 to 0.73")
            elif rule == "conflict_check":
                row.update(counts)
                implied = ei.counts_tuple(10, 100, 20, 100, "RR")
                row.update(effect=0.1 if positive else implied["estimate"], ci_low=implied["ci_low"], ci_high=implied["ci_high"])
            elif rule == "published_model":
                row["source"] = "age-adjusted Cox hazard ratio" if positive else "risk ratio"
            elif rule == "rate_ratio_labelled_as_rr":
                row.update(effect=0.83, ci_low=0.75, ci_high=0.93,
                           source="age-adjusted rate ratio, 0.83 (95% CI, 0.75 to 0.93)" if positive
                           else "relative risk, 0.83 (0.75-0.93)")
                # The abbreviated negative quotation has no CI token. Its
                # synthetic held sentence exercises the documented fallback.
                ab = row["source"] if positive else "relative risk, 0.83 (95% CI, 0.75-0.93)"
            row["id"] = f"__control_{rule}_{'positive' if positive else 'negative'}"
            row["label"] = row["id"]
            inputs = {"row": row, "spec": spec, "pool": [row, *peers], "abstract": ab,
                      "intervention": ["Drug"], "comparator": ["placebo"]}
            cases.append({"name": row["id"], "rule": rule, "expected_fire": positive,
                          "inputs": inputs, "result": evaluate(**inputs)[rule]})
    return cases


PREVIOUS = {
    "double zero": ("DoubleZero", 0, None),
    "polarity mismatch": ("polarity_check", 0, None),
    "undeclared shared control": ("apply_multi_arm_rule", 0, None),
    "counts under an HR target": ("count_only_under_hr", 0, None),
    "rate ratio labelled as RR": ("rate_ratio_labelled_as_rr", 2, 127),
    "transform provenance": ("transform_provenance", 2, 86),
    "HR-in-risk-pool": ("hr_route", 2, None),
    "OR reconstructed": ("reconstruct_from_counts", 1, 1),
    "source-effect conflicts": ("conflict_check", 3, 4),
}


def build_fixture(ref=PINNED):
    slugs, blobs, record_paths = pinned_inputs(ref)
    rows, outcomes = [], []
    for slug in slugs:
        review = blobs[f"docs/reviews/{slug}/review.json"]
        config = blobs[f"topics/{slug}.json"]
        specs = [config["primary_outcome"], *config.get("secondary_outcomes", []), *config.get("harm_outcomes", [])]
        recs = {str(r["id"]): r for r in blobs[record_paths[slug]]["records"]} if record_paths[slug] else {}
        for oi, outcome in enumerate(review["outcomes"]):
            matches = [s for s in specs if s["name"] == outcome["name"]]
            if len(matches) != 1:
                raise ValueError(f"{slug}/{outcome['name']}: expected exactly one pinned topic spec")
            spec = dict(matches[0])
            spec["selector_estimand"] = (outcome.get("estimand_decision") or {}).get("target_scale")
            trials = outcome.get("trials") or []
            outcomes.append({"slug": slug, "outcome": outcome["name"], "outcome_index": oi, "rows": len(trials)})
            for ri, t in enumerate(trials):
                pid = str(t.get("id", "")).replace("PMID ", "")
                ab = (recs.get(pid) or {}).get("abstract")
                reason = ("neither pinned cache path exists" if not record_paths[slug] else
                          "no held record matching pipeline id " + repr(pid) if pid not in recs else
                          "matching held record has no abstract" if not ab else None)
                rows.append({"slug": slug, "outcome": outcome["name"], "trial_id": t.get("id"),
                    "outcome_index": oi, "row_index": ri, "label": t.get("label"),
                    "served_scale": t.get("scale"), "target_estimand": spec.get("estimand"),
                    **evaluate(t, spec, trials, ab, list(config.get("intervention_terms", ["colchicine"])),
                               list(config.get("comparator_terms", ["placebo", "control"])), reason)})
    totals, unevaluable = {}, []
    for rule in DENOMINATORS:
        applicable = [r for r in rows if r[rule]["applicable"]]
        totals[rule] = {"fires": sum(r[rule]["fires"] is True for r in applicable), "of": len(applicable),
                        "kinds": dict(sorted(Counter(r[rule]["state"] for r in applicable).items()))}
        for r in rows:
            if r[rule]["state"] == "UNEVALUABLE":
                unevaluable.append({**identity(r), "rule": rule, "reason": r[rule]["reason"]})
    comparisons = {}
    for name, (rule, n, denominator) in PREVIOUS.items():
        total = totals[rule]
        incomplete = any(u["rule"] == rule for u in unevaluable)
        agrees = total["fires"] == n and (denominator is None or total["of"] == denominator)
        comparisons[name] = {"rule": rule, "previous": {"fires": n, "of": denominator}, "current": total,
            "status": "UNEVALUABLE" if incomplete else "AGREES" if agrees else "DISAGREES",
            "firing_rows": [identity(r) for r in rows if r[rule]["fires"] is True],
            "applicable_rows": [{**identity(r), "state": r[rule]["state"], "served_scale": r["served_scale"],
                                 "target_estimand": r["target_estimand"]} for r in rows if r[rule]["applicable"]],
            "unevaluable_rows": [identity(r) for r in rows if r[rule]["state"] == "UNEVALUABLE"]}
        if name == "OR reconstructed":
            subset = [r for r in rows if r[rule]["applicable"] and r["served_scale"] == "OR"]
            comparisons[name]["scope_explanation"] = (
                f"The prior OR-input-only scope reproduces {sum(r[rule]['fires'] is True for r in subset)}/{len(subset)}. "
                "The production guard also accepts other incompatible measures; all applicable rows are named below.")
        if name == "source-effect conflicts":
            subset = [r for r in rows if r[rule]["applicable"] and r[rule]["state"] != "NOT_COMPARABLE"]
            comparisons[name]["scope_explanation"] = (
                f"The prior comparable-ratio-only scope reproduces {sum(r[rule]['fires'] is True for r in subset)}/{len(subset)}. "
                "Two published HRs also reach conflict_check and return NOT_COMPARABLE; retained in the broader N.")
    return {"pinned": ref, "slugs": slugs, "outcomes": outcomes, "per_row": rows, "totals": totals,
            "denominators": DENOMINATORS, "record_paths": record_paths, "unevaluable": unevaluable,
            "controls": controls(), "comparisons": comparisons}


def identity(row):
    return {k: row[k] for k in ("slug", "outcome", "trial_id", "outcome_index", "row_index")}


def row_name(row):
    return f"{row['slug']} / {row['outcome']} / {row['trial_id']} [outcome {row['outcome_index']}, row {row['row_index']}]"


def markdown(data):
    lines = ["# Effect-identity pinned corpus fixture", "", f"Pinned source: `{data['pinned']}`.", "",
        f"Coverage: {len(data['slugs'])} served index pages, {len(data['outcomes'])} outcomes, {len(data['per_row'])} trial rows. "
        "Every outcome is inventoried, including those with no trials. Scope is outcomes[].trials[], not declared-absent/recovery inventories.", "",
        "This is an independent rule audit of frozen served inputs, not a sequential pipeline rebuild. "
        "Each probe uses the pipeline's arguments and applicability guard: pinned topic specification, row quotation, "
        "cache-first held abstract (docs/cache fallback), and complete same-outcome pool. Reconstruction, normalisation, "
        "and holding by one probe do not change another probe's inputs. Synthetic controls never enter totals or denominators. "
        "NOT_APPLICABLE reasons are retained on every row in JSON. UNEVALUABLE remains in N; fires counts only known positives.", "",
        "| Input | Static vs dynamic / hardcode disclosure |", "|---|---|",
        "| Commit, previous measurements, control examples | Static: explicitly supplied pin/comparators and synthetic controls |",
        "| Review rows, IDs, specifications, abstracts | Dynamic: read only from pinned git objects; no live network or guessed identifiers |",
        "| Rule outputs and totals | Dynamic: local production functions; no hardcoded research effects or counts |", "",
        "| Rule | Fires | N | What N counts / fire meaning |", "|---|---:|---:|---|"]
    for rule, total in data["totals"].items():
        lines.append(f"| {rule} | {total['fires']} | {total['of']} | {DENOMINATORS[rule]} |")
    lines += ["", "## Comparison with previous measurements", "",
              "An unevaluable comparison is not reported as agreement, even when the known-positive count matches.", ""]
    for name, c in data["comparisons"].items():
        old = c["previous"]
        lines.append(f"- {name}: **{c['status']}**; previous {old['fires']}" +
                     (f"/{old['of']}" if old['of'] is not None else "") +
                     f"; now {c['current']['fires']}/{c['current']['of']} known fires.")
        for row in c["firing_rows"]:
            lines.append(f"  - Fires: {row_name(row)}")
        if c.get("scope_explanation"):
            lines.append(f"  - Scope: {c['scope_explanation']}")
            for row in c["applicable_rows"]:
                lines.append(f"  - Evaluated: {row_name(row)}; {row['served_scale']} -> {row['target_estimand']}; {row['state']}")
        if c["unevaluable_rows"]:
            lines.append("  - Named unevaluable rows and reasons are listed below.")
    lines += ["", "## Unevaluable rows", "",
        "The rate-ratio probe uses extract._EFFECT and extract._effect_from_match with sentence context. "
        "It matches the served point and both CI ends (absolute tolerance 1e-6) in source/quotation/source_span, "
        "then falls back to held abstract sentences. Conflicting source types or missing matches are UNEVALUABLE. "
        "Rows with a quotation and a served scale other than RR cannot fire and remain in N. "
        "The synthetic negative control preserves the requested abbreviated quotation and supplies a synthetic "
        "held sentence with an explicit CI token, required by extract's regex, to exercise fallback. "
        "All unevaluable rows are named below with reasons.", ""]
    for u in data["unevaluable"]:
        lines.append(f"- **{u['rule']}**: {row_name(u)} — {u['reason']}")
    lines += ["", "## Non-comparable source effects", "",
              "These calls are evaluable as NOT_COMPARABLE, but cannot establish source-effect agreement; both stay in conflict_check N.", ""]
    for row in data["per_row"]:
        if row["conflict_check"]["state"] == "NOT_COMPARABLE":
            lines.append(f"- {row_name(row)} — {row['conflict_check']['detail']['reason']}")
    lines += ["", "## No typed CI available for se_permitted", "",
              "The following reported-effect rows contain no interval recognised by ci_representation. "
              "No typed CI can be passed to se_permitted. These named rows are outside its explicitly typed-CI denominator, "
              "but remain in the ci_representation and uncertainty_state denominators. This is a parser limitation, "
              "not a finding that the source lacks uncertainty.", ""]
    for row in data["per_row"]:
        if row["ci_representation"]["state"] == "NO_PARSED_CI":
            lines.append(f"- {row_name(row)} — {row['se_permitted']['reason']}")
    lines += ["", "## Reproduction", "", "```text",
        "python evidence/fixtures/build_effect_identity_fixture.py",
        "python -m pytest -q tests/test_effect_identity_corpus_fixture.py -p no:cacheprovider", "```", "",
        "The test compares recomputed JSON and Markdown, checks full inventory and denominator accounting, "
        "and checks each synthetic control independently. Missing pinned history is pytest.fail, never a skip.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    data = build_fixture()
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "effect_identity_corpus.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    (DEST / "EFFECT_IDENTITY_FIXTURE.md").write_text(markdown(data), encoding="utf-8")
    print(json.dumps(data["totals"], indent=2))
