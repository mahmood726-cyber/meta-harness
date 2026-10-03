"""Audit the k-gap SCREEN_OR_ELIGIBILITY rows: which exclusions FLIP under fixes already found, which are true.

Each row's records are re-screened IN MEMORY by the real harness screener (harness.screen.run over pipeline._dedup),
once per fix and once with all fixes, and the row's decision is compared with the unmodified screen. Nothing is
written to cache/, topics/ or docs/. Fixes (each a deterministic transform, not a judgement):

  F_HYPHEN     fold typographic dashes (U+2010-2015, U+2212) to '-' in the record's title/conditions/abstract.
               harness.lexicon.fold keeps U+2010, so 'Antibiotic‐associated' never matches 'antibiotic-associated'.
  F_PREVENTION condition-as-outcome: switch the screener's existing `prevention` semantics on for a topic whose
               population_any terms are also its primary-outcome keywords (the population term IS the outcome the
               trial prevents, so a prevention trial's title names who it enrolled, not the outcome).

A row that does not flip is classified by its rule into a typed true-exclusion class. The classifier is written by
the same author who reads its output: its classes are mechanical from the rule id and reason text and every row is
listed with its record span, so each can be checked by hand.

    python scripts/k_gap_screen_audit.py   -> outputs/k_gap/screen_audit.json
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "outputs", "k_gap")
_DASH = re.compile("[‐‑‒–—―−]")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def fold_dashes_rec(r):
    r = dict(r)
    for k in ("title", "abstract", "acronym"):
        if isinstance(r.get(k), str):
            r[k] = _DASH.sub("-", r[k])
    if isinstance(r.get("conditions"), list):
        r["conditions"] = [_DASH.sub("-", c) if isinstance(c, str) else c for c in r["conditions"]]
    return r


def condition_is_outcome(config):
    """population_any shares a term with the primary outcome's keywords (folded, '*' stripped)."""
    from harness import lexicon
    inc = config.get("include") or {}
    pop = {lexicon.fold(t).rstrip("*").strip() for t in (inc.get("population_any") or [])}
    kw = [lexicon.fold(k) for k in ((config.get("primary_outcome") or {}).get("keywords") or [])]
    return sorted(p for p in pop if p and any(p in k or k in p for k in kw))


def screen_decisions(slug, fix=()):
    from harness import pipeline, screen
    config = copy.deepcopy(_j(os.path.join(ROOT, "topics", slug + ".json")))
    records = copy.deepcopy(_j(os.path.join(ROOT, "cache", slug, "records.json")))
    if "F_HYPHEN" in fix:
        records["records"] = [fold_dashes_rec(r) for r in records.get("records", [])]
        records["ctgov"] = [fold_dashes_rec(r) for r in records.get("ctgov", [])]
    if "F_PREVENTION" in fix and condition_is_outcome(config):
        config["include"] = dict(config.get("include") or {}, prevention=True)
    merged = pipeline._dedup(records, config.get("pivotal_trials"))
    scr = screen.run(merged, config)
    return {d["id"]: d for d in scr["decisions"]}


def true_class(dec):
    rule, reason = dec.get("rule_id") or "", dec.get("reason") or ""
    if rule == "X2" and reason.startswith("wrong population"):
        return "SCOPE_POPULATION_EXCLUDED_BY_PROTOCOL"
    if rule == "X2":
        return "POPULATION_TERM_ABSENT_FROM_TITLE_CONDITIONS"
    if rule == "X3" and "randomised intervention is not" in reason:
        return "OTHER_AGENT_TRIAL (table drug label wrong)"
    if rule == "X3" and "wrong form" in reason:
        return "INTERVENTION_WRONG_FORM"
    if rule == "X3":
        return "COMPARATOR_TERM_ABSENT"
    if rule == "X-DESIGN":
        return "DESIGN_PROTOCOL (double-blind/context required)"
    if rule == "X1":
        return "NOT_RCT_BY_RECORD"
    if rule in ("X-DEDUP", "X-CONTRAST"):
        return "CORRECT_BY_DESIGN (" + rule + ")"
    return "OTHER:" + rule


def main():
    t = _j(os.path.join(OUT, "k_gap_table.json"))
    rows = [r for r in t["trials"] if r["gap_class"] == "SCREEN_OR_ELIGIBILITY"]
    fixes = {"BASE": (), "F_HYPHEN": ("F_HYPHEN",), "F_PREVENTION": ("F_PREVENTION",),
             "ALL": ("F_HYPHEN", "F_PREVENTION")}
    cache = {}
    out, tally, by_rule = [], Counter(), Counter()
    for r in rows:
        s = r["slug"]
        for name, fx in fixes.items():
            if (s, name) not in cache:
                cache[(s, name)] = screen_decisions(s, fx)
        base = {p: cache[(s, "BASE")].get(p) for p in r["pmids"] if cache[(s, "BASE")].get(p)}
        rec = {"slug": s, "label": r["label"], "unit_source": r["unit_source"], "drug": r["drug"],
               "pmids": r["pmids"][:4], "confirmed_member": r["unit_source"] != "REFERENCE_SEED" and r["drug"] != "OTHER_AGENT"}
        if not base:
            rec.update({"class": "NOT_SCREENED (no report of this trial in the screened corpus)", "flips_under": None})
        elif any(d["decision"] == "include" for d in base.values()):
            rec.update({"class": "INCLUDED_REPORT_EXISTS (gap is downstream of screening)", "flips_under": None})
        else:
            d0 = next(iter(base.values()))
            rec.update({"rule_id": d0.get("rule_id"), "reason": (d0.get("reason") or "")[:220], "span": (d0.get("span") or "")[:220]})
            flips = []
            for name in ("F_HYPHEN", "F_PREVENTION", "ALL"):
                after = [cache[(s, name)].get(p) for p in base]
                if any(a and a["decision"] == "include" for a in after):
                    flips.append(name)
                elif any(a and (a.get("rule_id"), a.get("reason")) != (d0.get("rule_id"), d0.get("reason")) for a in after):
                    a = next(a for a in after if a)
                    rec.setdefault("moved_to_other_exclusion", {})[name] = [a.get("rule_id"), (a.get("reason") or "")[:140]]
            rec["flips_under"] = flips or None
            rec["class"] = ("FLIPS_TO_INCLUDE:" + ("F_HYPHEN" if "F_HYPHEN" in flips else "F_PREVENTION" if "F_PREVENTION" in flips else "ALL_ONLY")) if flips else true_class(d0)
            by_rule[d0.get("rule_id")] += 1
        tally[rec["class"]] += 1
        out.append(rec)
    conf = [x for x in out if x["confirmed_member"]]
    res = {"n_rows": len(out), "n_confirmed_members": len(conf),
           "tally_all": dict(tally.most_common()), "tally_confirmed": dict(Counter(x["class"] for x in conf).most_common()),
           "by_rule_all": dict(by_rule), "condition_is_outcome_topics": {}, "rows": out}
    for s in sorted({x["slug"] for x in out}):
        cio = condition_is_outcome(_j(os.path.join(ROOT, "topics", s + ".json")))
        if cio:
            res["condition_is_outcome_topics"][s] = cio
    with open(os.path.join(OUT, "screen_audit.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ("n_rows", "n_confirmed_members", "tally_confirmed", "tally_all",
                                            "condition_is_outcome_topics")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
