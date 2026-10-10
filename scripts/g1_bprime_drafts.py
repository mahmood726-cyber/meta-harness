"""DRAFT B-prime-style endpoint-axis amendments for every (b) topic (Captain ruling 2, 10 Oct). Amending a protocol is
Mahmood's: these are DRAFTS for one V15 item, quoted against the CURRENT protocol text (verbatim), with the literal-rule
count measured by the concept search. Nothing is applied and no protocol file is touched.

Per topic: the registered primary outcome line (verbatim), the current outcome-axis paragraph (verbatim), the draft
sentence (the typed criterion: the outcome prespecified AND systematically ascertained as a primary or key-secondary
EFFICACY endpoint), the literal-rule universe (concept records the regex screen admits, not already held), and the
amended count (PENDING: it needs the recorded screen under the draft, which waits on the codex disk floor).

    python scripts/g1_bprime_drafts.py -> outputs/k_gap/v15_bprime_drafts.md
"""
from __future__ import annotations

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

B_TOPICS = ["dpp4-mace-t2d", "semaglutide-obesity-mace", "sglt2-hfref-hosp-cvdeath", "dapagliflozin-hfpef-hosp",
            "empagliflozin-hfpef-hosp", "finerenone-ckd-t2d-renal", "spironolactone-hfref-mortality",
            "denosumab-vertebral-fracture", "iv-iron-hfref-hosp", "sacubitril-valsartan-hfref", "sglt2-ckd-progression",
            "sglt2-primary-prevention-hf", "statins-primary-prevention-elderly", "noac-vs-warfarin-af-stroke"]


def primary_outcome(md):
    lines = md.splitlines()
    for i, l in enumerate(lines):
        if re.search(r"\*\*O \(primary\)\*\*|\*\*Primary outcome:\*\*", l):
            out = [l]
            for m in lines[i + 1:]:
                if not m.startswith("  ") or not m.strip():
                    break
                out.append(m)
            return " ".join(x.strip() for x in out)
    return None


def outcome_phrase(po):
    t = re.sub(r"^-\s*\*\*[^*]+\*\*\s*[-:]?\s*", "", po or "").strip().rstrip(".")
    return t[0].lower() + t[1:] if t else "(the registered primary outcome)"


def main():
    import g1_v14_axis_question as ax
    g1 = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "G1_TRACKER.json"), encoding="utf-8"))
    g1 = g1.get("topics") or g1
    w = ["# V15 item (DRAFT): B-prime-style endpoint-axis amendments for the (b) topics -- Captain ruling 2", "",
         "Amending a protocol is Mahmood's; every sentence below is a DRAFT, quoted against the current protocol text. "
         "The typed criterion mirrors GLP-1's signed B-prime (operating reading (ii)): the topic's registered primary "
         "outcome, or its exact components, PROSPECTIVELY SPECIFIED AND SYSTEMATICALLY ASCERTAINED as a PRIMARY or "
         "KEY-SECONDARY EFFICACY endpoint of the trial. Safety-only adjudication does not meet it.", "",
         "Literal universe = concept-search records not already held that the regex screen admits under the current "
         "P/I/C/design rule (outputs/k_gap/v14_question_eligibility_axis.md). Amended count = PENDING (the recorded "
         "dual screen under the draft; codex is at LEVEL 0 on the 5 GB disk floor, C: 4.93 GB).", "",
         "**Recommended default:** adopt the draft for every (b) topic. Each topic's served set is already its outcome "
         "trials, so the amendment changes no served pool and no G1 status today; it closes the literal-rule flood "
         "(the eligible-not-pooled set would otherwise hold every glycaemic / biomarker / dose-finding trial of the drug).", ""]
    for slug in B_TOPICS:
        md = open(os.path.join(ROOT, "protocols", f"{slug}.md"), encoding="utf-8").read()
        po = primary_outcome(md)
        axis = ax.axis_paragraph(md)
        scr = os.path.join(ROOT, "outputs", "k_gap", "concept", f"{slug}.screen.json")
        lit = len(json.load(open(scr, encoding="utf-8"))["includes"]) if os.path.exists(scr) else None
        st = (g1.get(slug) or {}).get("g1_status")
        w += [f"## {slug}  (G1 today: {st})", "",
              "Registered primary outcome (verbatim):", "", "> " + (po or "(not found)"), "",
              "Current outcome-axis text (verbatim):", ""]
        w += (["> " + x.lstrip("> ") for x in axis.splitlines()] if axis else ["> (none)"]) + [""]
        w += ["**Draft amendment sentence:**", "",
              f"> **Eligibility (B-prime style, DRAFT).** Trials meeting the registered P/I/C/design rule **in which "
              f"{outcome_phrase(po)}, or its exact components, was prospectively specified and systematically "
              f"ascertained as a primary or key-secondary efficacy endpoint**. A trial whose outcome was ascertained "
              f"only as an adverse event or under safety adjudication is outside. If the outcome was specified and "
              f"ascertained but its result is unavailable, the trial is retained as target-result absent.", "",
              f"- literal-rule universe (regex includes, not already held): **{lit}**",
              "- amended count: PENDING (recorded screen under the draft; codex disk floor)",
              f"- G1 effect: none on today's status ({st}) under the draft; under the LITERAL rule the {lit} records "
              "would enter screening and every eligible one outside the comparator would need a name.", ""]
    out = os.path.join(ROOT, "outputs", "k_gap", "v15_bprime_drafts.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(w) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
