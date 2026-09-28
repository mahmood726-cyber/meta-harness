"""Metformin-PCOS fixtures, 2026-09-28.
 (1) Moll 2006 (PMID 16769748, BMJ): discontinuation due to side effects. The abstract gives percentages and a risk
     difference ('16% v 5%; 11%, 5% to 16%'), so the pinned EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH refusal stands (it is
     an HM3 control entry and is NOT edited) and the state is REPORTED_UNRESOLVED -- never absent. The full report's
     18/111 vs 6/114 (repeated in the investigators' later report, a corroborating report of the same trial) is recorded
     in docs/relayed_values.json as RELAYED, NOT HELD: the BMJ PDF answered 403 and the PMC copy a bot-check page
     (recorded, neither retried nor worked around); the committed ft_16769748.txt is front matter + abstract only.
     It belongs to 'Treatment discontinuation due to adverse events' ONLY; the GI row is SIGNAL_SPURIOUS -> not reported.
 (2) The family invariant (harness/family_invariant.py) is enforced in code; nothing to declare here.
  PYTHONPATH=. python outputs/handover/metformin_sources/make_metformin_fixtures.py"""
import json, os

p = "docs/relayed_values.json"
d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {
    "_doc": ("Values RELAYED to the evidence lane that are NOT verified against held bytes (the source is not openly held). "
             "Read by harness/relayed_values.py and shown beside their row; NEVER data: never pooled, never a count, "
             "until the source is held and the value is bound. Recorded by the evidence lane (Claude Opus 5.5)."),
    "values": []}
d["values"] = [v for v in d["values"] if not (v["topic"] == "metformin-pcos-ovulation" and v["trial"] == "PMID 16769748")]
d["values"].append({
    "topic": "metformin-pcos-ovulation", "trial": "PMID 16769748", "outcome": "Treatment discontinuation due to adverse events",
    "value": "18/111 metformin vs 6/114 placebo (discontinuation due to side effects)",
    "relayed_by": "the orchestrating lane (metformin-PCOS review fixtures, 2026-09-28)",
    "said_to_be_in": "the BMJ full report and the investigators' later report of the same trial",
    "why_not_held": ("BMJ PDF (www.bmj.com) answered 403; the PMC copy (PMC1482338) answered a bot-check page; Europe PMC: "
                     "not in the open-access subset; the committed ft_16769748.txt is front matter + abstract only. "
                     "Recorded in evidence/acquisition_cascade/ATTEMPTS.jsonl (targets Moll2006, Moll-later)."),
    "not_for": ["Gastrointestinal adverse events"]})
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("docs/relayed_values.json: Moll discontinuation relayed-not-held")
