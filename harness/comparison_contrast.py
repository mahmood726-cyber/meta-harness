"""COMPARISON-LEVEL contrast (V1.0.1, SGLT2-HFrEF review).

NCT04385589 (Ibrahim; PMID 33426003) was screened "eligible double-blind/placebo-controlled" because its registry names
an arm "Placebo group" -- but that arm's only registered intervention is insulin, the same insulin the dapagliflozin
arm receives as background. The randomised contrast is dapagliflozin + insulin versus insulin: add-on versus
background, with no placebo. A protocol that requires a placebo comparator is not met by an arm LABEL.

The registry cannot settle it alone: it types that arm PLACEBO_COMPARATOR and declares double masking, and many real
placebo arms register no placebo product (VERTIS CV's "Placebo: glycemic rescue"). The refusal therefore needs three
facts, and refuses only when all hold:
  1. every comparator arm (an arm without the topic intervention) receives nothing but interventions that are
     background in the experimental arm (the family's registered arms, harness/trial_family);
  2. none of those interventions is a placebo / sham / dummy / vehicle;
  3. the trial's OWN held publication (a report of the family) never mentions placebo, blinding or masking.
A family with no held publication cannot be refused here.
"""
from __future__ import annotations

from typing import Optional

RULE = "X3-CONTRAST"
PLACEBO_LIKE = ("placebo", "sham", "dummy", "vehicle", "matching")


_TRIAL_BLIND = ("placebo", "blind", "masked", "masking", "sham", "dummy")


def refusal(node: dict, config: dict, report_text=lambda rid: None) -> Optional[dict]:
    inc = config.get("include") or {}
    if "placebo" not in [str(x).lower() for x in inc.get("comparator_any") or []]:
        return None
    terms = [str(t).lower() for t in (inc.get("intervention_any") or []) + (config.get("intervention_terms") or [])]
    arms = node.get("arms") or []
    names = lambda a: [str(x).lower() for x in a.get("active_interventions") or []]  # noqa: E731
    exp = [a for a in arms if any(t in n for n in names(a) for t in terms)]
    ctl = [a for a in arms if a not in exp]
    if not exp or not ctl:
        return None
    background = {str(x).lower() for a in exp for x in a.get("background_therapy") or []}
    for a in ctl:
        n = names(a)
        if not n or any(p in x for x in n for p in PLACEBO_LIKE) or not set(n) <= background:
            return None
    pubs = [(r["report_id"], report_text(r["report_id"])) for r in node.get("reports") or []
            if str(r.get("report_id") or "").isdigit()]
    pubs = [(rid, t) for rid, t in pubs if t]
    if not pubs or any(w in t.lower() for _, t in pubs for w in _TRIAL_BLIND):
        return None
    lab = lambda a: str((a.get("label") or {}).get("value") or "")  # noqa: E731
    return {"rule_id": RULE,
            "reason": ("comparison-level contrast: the comparator arm" + ("s " if len(ctl) > 1 else " ")
                       + ", ".join(f"'{lab(a)}' ({', '.join(names(a))})" for a in ctl)
                       + " receive only the experimental arm's background therapy, no placebo product is registered, and "
                       f"the trial's own report (PMID {', '.join(r for r, _ in pubs)}) mentions neither placebo nor "
                       "blinding; the randomised contrast is add-on versus background, not the protocol's intervention "
                       "versus placebo (an arm LABEL is not a placebo)"),
            "span": "; ".join(f"{lab(a)}: {', '.join(names(a))}" for a in arms)}


def apply(scr: dict, family_nodes: list, config: dict, report_text=lambda rid: None) -> list:
    """Replace an INCLUDE (or a design-level X1) of any record of a refused family with the comparison-level refusal.
    Returns the refused family ids."""
    refused = {}
    for node in family_nodes or []:
        r = refusal(node, config, report_text)
        if r:
            for rep in node.get("reports") or []:
                refused[str(rep.get("report_id"))] = (node.get("family_id"), r)
    hit = set()
    for d in scr.get("decisions") or []:
        x = refused.get(str(d.get("id")))
        if x and (d.get("decision") == "include" or d.get("rule_id") == "X1"):
            d.update(decision="exclude", rule_id=x[1]["rule_id"], reason=x[1]["reason"], span=x[1]["span"])
            hit.add(x[0])
    return sorted(hit)
