"""Proposed P5 fix, executed in memory over EVERY trial family of the 24 reviews that carry an audited notice.

  FIX-A (code, harness/trial_family.py:345, screen_family population test): fold both sides with
        harness.lexicon.fold (the fold screening already uses); a term ending in '*' matches as a prefix (the
        protocol's own truncation, which PubMed honours at search time); a registry condition written in MeSH
        inverted form 'X, Y' is also read as 'Y X'. Monotone: it only ADDS matches to the current substring test.
  FIX-B (code, harness/trial_family.py:99, randomised_contrasts): a pair whose arms differ by the agent on one
        side and a DECLARED comparator (config include.comparator_any) on the other, with identical remaining
        (background) interventions, is a randomised contrast. The current rule accepts only pairs that differ by
        the agent alone, so no drug-vs-active-drug trial can ever pass.
  CONFIG-C (protocol data -- Mahmood's scientific call, not code): the registry's own wording added to the terms:
        esketamine population += 'depressive disorder, treatment-resistant'; dapagliflozin-hfpef population +=
        'preserved systolic function'; dpp4 agents += 'omarigliptin'. (A saline-as-comparator item was tried
        and dropped: it readmits nothing and would only change N08's reason.)

For every family: the screen as served (stored contrasts), a CONTROL re-derivation with the ORIGINAL function from
the arms (must reproduce the stored result), then FIX-A+B, then FIX-A+B+CONFIG-C. Prints every flip, targeted or not.
"""
import copy
import itertools
import json
import re
import subprocess
import sys
from pathlib import Path

W = Path(r"C:/mh-lanes/nr/wt")
sys.path.insert(0, str(W))
from harness import lexicon, trial_family  # noqa: E402

REV = "1fa77f2c4852ee79e55d540083e3c35bbff0cecc"
CONFIG_C = {
    "esketamine-trd-madrs": {"population_any": ["depressive disorder, treatment-resistant"]},
    "dapagliflozin-hfpef-hosp": {"population_any": ["preserved systolic function"]},
    "dpp4-mace-t2d": {"intervention_any": ["omarigliptin"]},
}


def show(path):
    return subprocess.run(["git", "show", f"{REV}:{path}"], cwd=W, capture_output=True, check=True).stdout


def _hit(term, values):
    t = re.escape(term.lower())
    return {v for v in values if re.search(r"(?<!\w)" + t + r"(?!\w)", v)}


def contrasts_fixed(arms, agents, comparators, randomized=False):
    """FIX-B: the original rule, plus agent-vs-declared-comparator pairs with identical background."""
    out = trial_family.randomised_contrasts(arms, agents, randomized)
    if not randomized:
        return out
    seen = {tuple(c["arm_ids"]) + (c["drug"],) for c in out}
    for a, b in itertools.permutations(arms, 2):
        if not a.get("linkage_complete") or not b.get("linkage_complete"):
            continue
        av, bv = set(a["active_interventions"]), set(b["active_interventions"])
        for agent in agents:
            aa, ab = _hit(agent, av), _hit(agent, bv)
            if not aa or ab:
                continue
            cb = set().union(*[_hit(c, bv) for c in comparators]) if comparators else set()
            ca = set().union(*[_hit(c, av) for c in comparators]) if comparators else set()
            if not cb or ca or av - aa != bv - cb:
                continue
            key = tuple(sorted([a["arm_id"], b["arm_id"]])) + (agent,)
            if key in seen:
                continue
            seen.add(key)
            out.append({"arm_ids": [a["arm_id"], b["arm_id"]], "drug": agent, "comparator": sorted(cb),
                        "background_therapy": sorted(av - aa), "span": [a.get("span"), b.get("span")]})
    return out


def pop_texts(conditions):
    texts = []
    for c in conditions:
        f = lexicon.fold(str(c))
        texts.append(f)
        if ", " in f:
            head, tail = f.split(", ", 1)
            texts.append(tail + " " + head)
    return " | ".join(texts)


def screen_fixed(family, config):
    """FIX-A: run the real screen_family with the population test replaced (by pre-matching)."""
    inc = config.get("include") or {}
    conditions = (family.get("population", {}).get("conditions") or {}).get("value") or []
    text = pop_texts(conditions)
    terms = [lexicon.fold(t) for t in inc.get("population_any") or []]
    ok = any((t[:-1] in text) if t.endswith("*") else (t in text) for t in terms)
    cfg = copy.deepcopy(config)
    if inc.get("population_any") and ok and conditions:
        # the real function does `any(t.lower() in text for t in population_any)` on the joined conditions;
        # hand it a term it will find, so every OTHER step of the real screen still runs unchanged
        cfg["include"]["population_any"] = [" ".join(conditions).lower()]
    return trial_family.screen_family(family, cfg)


def state(c):
    return (c.get("state"), c.get("absence_code") or c.get("code"))


audit = json.loads((W / "registry/notice_adjudication.json").read_text(encoding="utf-8"))
slugs = sorted({r["slug"] for r in audit["notices"]})
departing = {(r["slug"], t["family_id"]) for r in audit["notices"] for t in r["departing_trials"]}
rows, control_bad = [], []
for slug in slugs:
    review = json.loads(show(f"docs/reviews/{slug}/review.json"))
    topic = json.loads(show(f"topics/{slug}.json"))
    base = trial_family.protocol_requirements(str(W), slug, dict(topic))
    for variant in ("served", "control", "fixAB", "fixABC"):
        pass
    cfg_c = copy.deepcopy(base)
    for k, extra in CONFIG_C.get(slug, {}).items():
        cfg_c.setdefault("include", {}).setdefault(k, [])
        cfg_c["include"][k] = list(cfg_c["include"][k]) + extra
    for fam in review.get("trial_families") or []:
        if not fam.get("arms") and not fam.get("population"):
            continue
        arms = [dict(a, span=None) for a in fam.get("arms") or [] if a.get("active_interventions") is not None]
        randomized = bool(fam.get("randomised_contrasts")) or str(
            (fam.get("registry_design") or {}).get("allocation", "")).upper() == "RANDOMIZED"
        served = state(trial_family.screen_family(copy.deepcopy(fam), base))
        f0 = copy.deepcopy(fam)
        agents = list((base.get("include") or {}).get("intervention_any") or base.get("intervention_terms") or [])
        f0["randomised_contrasts"] = trial_family.randomised_contrasts(arms, agents, randomized)
        control = state(trial_family.screen_family(f0, base))
        if control != served:
            control_bad.append((slug, fam["family_id"], served, control))
        results = {}
        for name, cfg in (("fixAB", base), ("fixABC", cfg_c)):
            f1 = copy.deepcopy(fam)
            inc = cfg.get("include") or {}
            ag = list(inc.get("intervention_any") or cfg.get("intervention_terms") or [])
            f1["randomised_contrasts"] = contrasts_fixed(arms, ag, list(inc.get("comparator_any") or []), randomized)
            results[name] = state(screen_fixed(f1, cfg))
        rows.append({"slug": slug, "family": fam["family_id"], "departing": (slug, fam["family_id"]) in departing,
                     "served": served, "control": control, **results})

print(f"families screened: {len(rows)} across {len(slugs)} reviews; control mismatches: {len(control_bad)}")
for c in control_bad[:10]:
    print("  CONTROL MISMATCH", c)
for name in ("fixAB", "fixABC"):
    flips = [r for r in rows if r[name] != r["served"]]
    print(f"\n{name}: {len(flips)} families change state")
    for r in flips:
        print(f"  {'DEPARTING' if r['departing'] else 'other    '} {r['slug']} {r['family']}: {r['served']} -> {r[name]}")
Path(r"C:/mh-lanes/nr/work/fix_sweep.json").write_bytes(json.dumps(rows, indent=1).encode())
