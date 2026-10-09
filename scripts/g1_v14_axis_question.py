"""V14 QUESTION for the Captain: each active topic's ELIGIBILITY AXIS, quoted verbatim from its registered protocol, beside
the LITERAL-RULE UNIVERSE the concept search measured (records the regex screen admits under the protocol's own P/I/C/design
rule that the harness does not already hold). No trial is screened to eligible on a CVOT-style topic until this is answered
(user caution 9 Oct: 'Do not mark glycaemic trials eligible on PICO alone').

    python scripts/g1_v14_axis_question.py -> outputs/k_gap/v14_question_eligibility_axis.md
"""
from __future__ import annotations

import datetime
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "outputs", "k_gap", "concept")

# PROPOSED split (the Captain confirms or changes it): (a) the protocol's outcome is measured in essentially every trial its
# P/I/C rule admits, so a recorded dual screen can decide eligibility; (b) CVOT/event-style -- the literal rule admits every
# trial of the drug in the population, most of which never ascertained the outcome, so the universe is a V14 question.
SPLIT = {
    "doac-vte-recurrence": "a (at risk: phase-2 / biomarker trials admitted)", "noac-vs-warfarin-af-stroke": "b (moved 9 Oct: dual screen admitted 41 incl. cognition / plaque / biomarker trials)", "tranexamic-acid-pph": "a",
    "corticosteroids-covid19-mortality": "a", "colchicine-recurrent-pericarditis": "a",
    "melatonin-primary-insomnia-sol": "a", "esketamine-trd-madrs": "a", "semaglutide-obesity-weight": "a",
    "glp1-ra-mace-t2d": "b (B-prime amendment)", "dpp4-mace-t2d": "b", "semaglutide-obesity-mace": "b",
    "sglt2-hfref-hosp-cvdeath": "b", "dapagliflozin-hfpef-hosp": "b", "empagliflozin-hfpef-hosp": "b",
    "finerenone-ckd-t2d-renal": "b", "spironolactone-hfref-mortality": "b", "denosumab-vertebral-fracture": "b",
    "iv-iron-hfref-hosp": "b", "sacubitril-valsartan-hfref": "b", "sglt2-ckd-progression": "b",
    "sglt2-primary-prevention-hf": "b", "statins-primary-prevention-elderly": "b",
}


def axis_paragraph(md):
    """The protocol's own outcome-axis paragraph, verbatim (from the 'NOT on the outcome axis' sentence to the blank line)."""
    lines = md.splitlines()
    for i, l in enumerate(lines):
        if "NOT on the outcome axis" in l:
            out = []
            for m in lines[i:]:
                if not m.strip() or m.strip() == ">":
                    break
                out.append(m)
            return "\n".join(out)
    return None


def main():
    today = datetime.date.today().isoformat()
    w = [f"# V14 question -- the eligibility axis of each active topic (k-gap, {today})", "",
         "Writer: scripts/g1_v14_axis_question.py. Every quotation below is VERBATIM from protocols/<slug>.md.", "",
         "## 1. GLP-1 (glp1-ra-mace-t2d): the B-prime sentence and its disclosure", ""]
    g = open(os.path.join(ROOT, "protocols", "glp1-ra-mace-t2d.md"), encoding="utf-8").read().splitlines()
    bp = [(i + 1, l) for i, l in enumerate(g) if "prospectively specified and systematically ascertained" in l
          or "B-prime yields" in l]
    for n, l in bp:
        w += [f"protocols/glp1-ra-mace-t2d.md line {n}:", "", "> " + l.lstrip("> "), ""]
    w += ["**The question.** The FDA 2008 guidance made sponsors of glycaemic phase 3 programmes prospectively adjudicate "
          "MACE as a safety endpoint, so many glycaemic RCTs (SUSTAIN-1, PIONEER-1, AWARD-8, ...) literally satisfy "
          "'3-point MACE ... prospectively specified and systematically ascertained'. The disclosure line names exactly "
          "those trials as OUTSIDE ('B-prime yields the intended small universe'). Which governs: (i) the literal criterion "
          "-- every trial with prospectively adjudicated MACE, safety-adjudication included; or (ii) the intended universe "
          "-- MACE as a prespecified efficacy/primary or key secondary endpoint of a CV outcome trial? Until answered, "
          "no GLP-1 concept record is screened to eligible. The first dual run (PICO-only prompt, ~1,124 calls) is VOID "
          "(outputs/k_gap/concept/glp1-ra-mace-t2d.dual.VOID_pico_only_prompt.json) and decides nothing.", "",
          "## 2. Every active topic: axis sentence, literal-rule universe, proposed split", "",
          "Literal universe = concept-search records NOT already held that the regex screen INCLUDES under the protocol's "
          "own P/I/C/design rule (with the fixed-rule overlay). It counts records, not trials. Topics marked "
          "'pending' are still in the search queue; Europe PMC and EU CTR are being re-paged for the first 8 topics, so "
          "their counts can rise (the recall limit is recorded per source as `recall_limit`).", "",
          "| topic | split | new records | literal-rule includes | search state |", "|---|---|---|---|---|"]
    paras = []
    for slug, sp in SPLIT.items():
        led, scr = os.path.join(CON, f"{slug}.json"), os.path.join(CON, f"{slug}.screen.json")
        if os.path.exists(scr):
            s = json.load(open(scr, encoding="utf-8"))
            L = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
            qs = L.get("queries") or L.get("sources") or []
            st = "; ".join(f"{q.get('source')} {q.get('state')}" for q in qs if isinstance(q, dict) and
                           q.get("state") != "COMPLETE") or "all COMPLETE"
            w.append(f"| {slug} | {sp} | {s['n_records']} | {len(s['includes'])} | {st} |")
        else:
            w.append(f"| {slug} | {sp} | pending | pending | queued |")
        md = open(os.path.join(ROOT, "protocols", f"{slug}.md"), encoding="utf-8").read()
        paras.append((slug, axis_paragraph(md)))
    w += ["", "**Proposed rule.** (a) topics: a recorded dual codex screen with the protocol's eligibility text quoted "
          "verbatim decides eligibility. (b) topics: the literal-rule universe is reported here and NOT screened to "
          "eligible -- each protocol says eligibility is not on the outcome axis, so read literally every trial of the "
          "drug in the population is eligible, and 'eligible, not pooled' would flood with trials that never measured "
          "the outcome (the defect B-prime fixed for GLP-1). The Captain decides per topic: a B-prime-style amendment, "
          "or the literal universe. dpp4 is the clearest case: its search is UID queries for the 5 DPP-4 CVOTs, the same "
          "search-vs-eligibility mismatch B-prime fixed for GLP-1, and it has no amendment.", "",
          "## 3. The axis paragraph of each protocol, verbatim", ""]
    for slug, p in paras:
        w += [f"**{slug}**", ""] + (["> " + x.lstrip("> ") for x in p.splitlines()] if p else
                                    ["(no 'NOT on the outcome axis' sentence in this protocol)"]) + [""]
    out = os.path.join(ROOT, "outputs", "k_gap", "v14_question_eligibility_axis.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(w) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
