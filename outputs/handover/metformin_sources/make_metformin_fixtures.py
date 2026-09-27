"""Metformin-PCOS fixtures, 2026-09-28.
 (1) Moll 2006 (PMID 16769748, BMJ): discontinuation due to side effects. The abstract gives percentages and a risk
     difference ('16% v 5%; 11%, 5% to 16%'), so EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH stands and the state is
     REPORTED_UNRESOLVED -- never absent. The full report's 18/111 vs 6/114 (repeated in the investigators' later report,
     a corroborating report of the same trial) is RELAYED, not held: the BMJ PDF answered 403 and the PMC copy a bot-check
     page (recorded, neither retried nor worked around); the committed ft_16769748.txt is front matter + abstract only.
     The row belongs to 'Treatment discontinuation due to adverse events' ONLY; its gastrointestinal row is
     SIGNAL_SPURIOUS (the mention is of discontinuation, not GI incidence) and reads 'not reported'.
 (2) The family invariant (harness/family_invariant.py) is enforced in code; nothing to declare here.
  PYTHONPATH=. python outputs/handover/metformin_sources/make_metformin_fixtures.py"""
import json

vep = "cache/metformin-pcos-ovulation/verified_effects.json"
raw = open(vep, encoding="utf-8").read()
ve = json.loads(raw)
SPAN = ("A significantly larger proportion of women in the metformin group discontinued treatment because of side effects "
        "(16% v 5%; 11%, 5% to 16%).")
ab = next(r for r in json.load(open("cache/metformin-pcos-ovulation/records.json", encoding="utf-8"))["records"]
          if str(r["id"]) == "16769748")["abstract"]
assert SPAN in ab
rows = ve["16769748"] if isinstance(ve["16769748"], list) else [ve["16769748"]]
for r in rows:
    if r.get("outcome") == "Treatment discontinuation due to adverse events":
        r["reported_unresolved_span"] = SPAN
        r["relayed_not_held"] = {
            "values": "18/111 metformin vs 6/114 placebo (discontinuation due to side effects)",
            "relayed_by": "the orchestrating lane (metformin-PCOS review fixtures, 2026-09-28)",
            "said_to_be_in": "the BMJ full report (Table) and the investigators' later report of the same trial",
            "why_not_held": ("BMJ PDF (www.bmj.com) answered 403; the PMC copy (PMC1482338) answered a bot-check page; "
                             "Europe PMC: not in the open-access subset; the committed ft_16769748.txt is front matter + "
                             "abstract only (publisher disallows XML full text). Recorded in "
                             "evidence/acquisition_cascade/ATTEMPTS.jsonl (targets Moll2006, Moll-later)."),
            "policy": "not data: never pooled, never rendered as a count, until the table is held"}
        r["reason"] = ("REPORTED, not resolved: the abstract gives discontinuation because of side effects as percentages "
                       "and a risk difference (16% v 5%; 11%, 5% to 16%), not the counts the registered RR needs. The full "
                       "report's counts are not openly held (see relayed_not_held).")
open(vep, "w", encoding="utf-8", newline="\n").write(json.dumps(ve, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))
print("Moll discontinuation row: reported-unresolved span + relayed-not-held record")
