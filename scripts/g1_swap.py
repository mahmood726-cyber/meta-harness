"""PRE-REGISTERED COMPARATOR SWAPS (Mahmood 6 Oct: "solve it through comparator swaps"), the 5 Oct process as a
reproducible harness. Stages, each a subcommand:

  rules SLUG...      write registry/comparator_selection/<slug>.rule.json from the topic's OWN protocol fields
                     (topics/<slug>.json: question, eligibility, intervention/comparator terms, primary outcome, estimand,
                     timepoint). Commit + push BEFORE any search: the rule's git SHA is the pre-registration.
  search SLUG...     recorded literature search (PubMed esearch + Europe PMC, response sha256 kept)
  screen SLUG...     C1 mechanically (licence CC BY / CC0 from Europe PMC, else Unpaywall); C2-C6 per C1-passing candidate
                     by ONE recorded codex call over the candidate's held CC BY text, every PASS gated on a verbatim quote
  select SLUG...     scripts/g1_comparator_select.py (deterministic: the rule alone)

Rule R0 (the "blocks a match" test, decided before any search): the CURRENT comparator is assessed against C1-C6 by the
same procedure; it is retired only when it FAILS at least one criterion (recorded with that criterion's evidence); when
it passes all six it is KEPT (NO_SWAP: the block is acquisition, not the comparator) and no replacement is chosen.
How our own pool compares with any candidate is never an input.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
SEL = os.path.join(ROOT, "registry", "comparator_selection")
RATIO = {"HR", "RR", "OR"}


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def protocol(slug):
    """The protocol fields a rule quotes, taken from the topic file only."""
    c = _j(os.path.join(ROOT, "topics", slug + ".json"))
    po = c.get("primary_outcome") or {}
    est = (po.get("estimand") or "").upper()
    return {"file": f"topics/{slug}.json", "question": c.get("question") or c.get("title"),
            "eligibility": c.get("eligibility_summary") or None,
            "intervention_terms": c.get("intervention_terms") or [], "comparator_terms": c.get("comparator_terms") or [],
            "primary_outcome": po.get("name"), "estimand": est, "timepoint": po.get("timepoint"),
            "analysis_population": po.get("population"), "current_comparator": str(c.get("comparator_pmid"))}


def rule(slug):
    p = protocol(slug)
    est = p["estimand"]
    fam = ("ratio (HR, RR or OR)" if est in RATIO else f"{est} (a standardised difference fails)")
    t1 = (f"1 = {est}; 0 = another ratio" if est in RATIO else f"1 = {est} on the protocol's scale; 0 = other")
    return {
        "slug": slug,
        "purpose": ("PRE-REGISTERED selection rule for a replacement comparator meta (Mahmood 6 Oct: 'solve it through "
                    "comparator swaps'). Committed BEFORE any candidate search; candidates are judged per criterion from "
                    "their own text, and the pick follows from R0, the criteria and the tie-breaks alone. How our pool "
                    "compares with any candidate is NOT an input."),
        "protocol_reference": p,
        "R0_current_comparator": {
            "comparator_pmid": p["current_comparator"],
            "test": ("the current comparator is assessed against C1-C6 by the same procedure as every candidate. It is "
                     "RETIRED only if it fails at least one criterion (reason = that criterion, span = its evidence); if it "
                     "passes all six it is KEPT and the topic is NO_SWAP (the block is acquisition, not the comparator)."),
            "excluded_from_candidates_when_retired": True},
        "criteria": [
            {"id": "C1_OPEN_LICENCE", "pass_if": "the meta's full text is held under CC BY or CC0 (Europe PMC licence field, "
                                                  "else the Unpaywall location licence); any other licence, or free-to-read "
                                                  "without a licence, fails (lane licence rule)"},
            {"id": "C2_RCT_ONLY", "pass_if": "the analysis pools randomised controlled trials only (its own eligibility / "
                                             "methods statement)"},
            {"id": "C3_POPULATION", "pass_if": f"the pooled analysis is in the protocol's population: {p['question']}"
                                               + (f" (eligibility: {p['eligibility']})" if p["eligibility"] else "")},
            {"id": "C4_INTERVENTION_VS_COMPARATOR",
             "pass_if": f"the pooled comparison is {' / '.join(p['intervention_terms'][:6])} versus "
                        f"{' / '.join(p['comparator_terms'][:6])}"},
            {"id": "C5_OUTCOME_AND_ESTIMAND", "pass_if": f"it pools {p['primary_outcome']} (protocol timepoint: "
                                                         f"{p['timepoint']}) on the estimand family {fam}"},
            {"id": "C6_ROWS_AND_POOLED", "pass_if": "it prints per-trial rows for that outcome (a table, or a forest plot "
                                                    "with counts or effects, in the article or its own open supplement) AND "
                                                    "a pooled result for it"}],
        "tie_breaks": [
            {"id": "T1_ESTIMAND_MATCH", "order": "descending", "score": t1},
            {"id": "T2_MOST_RECENT", "order": "descending", "score": "publication year, then month"},
            {"id": "T3_LARGEST_K", "order": "descending", "score": "number of trials in the pooled analysis of the protocol outcome"}],
        "if_none_pass": ("NO_ACHIEVABLE_COMPARATOR: record the closest candidate and its single failing criterion; the "
                         "topic keeps its current comparator; no criterion is relaxed after the search"),
        "selector": "scripts/g1_comparator_select.py (deterministic; reads this rule and the typed candidates file)",
        "candidates_file": f"registry/comparator_selection/{slug}.candidates.json",
        "process": "scripts/g1_swap.py (rules -> search -> screen -> select); enumeration and acquisition follow the pick"}


def cmd_rules(slugs):
    for s in slugs:
        p = os.path.join(SEL, f"{s}.rule.json")
        if os.path.exists(p):
            old = _j(p)
            if old.get("process", "").startswith("scripts/g1_swap.py"):
                print(s, "rule exists (kept: a pre-registration is never rewritten)")
                continue
            raise SystemExit(f"{s}: a rule from an earlier round exists ({p}); refusing to overwrite a pre-registration")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rule(s), fh, indent=1, ensure_ascii=False)
        print(s, "rule written")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cmd, *args = sys.argv[1:]
    {"rules": cmd_rules}[cmd](args)
