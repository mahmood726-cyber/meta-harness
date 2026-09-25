"""Judgement B2 verdicts: B1 unchanged in every field it had, plus, per departing trial, the constraint that actually
failed the admission check (lane label recorded before the blind second read; sha256 346c8d4b...) and the second
reader's bucket. Same pinned bytes as B1."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:/mh-lanes/nr/wt")
from scripts import notice_rejudge as rj  # noqa: E402
from scripts import notice_anchor as anchor  # noqa: E402

WORK = Path(r"C:/mh-lanes/nr/work")
b1 = json.loads((WORK / "verdicts_b1.json").read_text(encoding="utf-8"))
mine = json.loads((WORK / "lane_classes.json").read_text(encoding="utf-8"))
sub = json.loads((WORK / "c02_subagent_answer.json").read_text(encoding="utf-8"))["items"]
BUCKET = {"ACTIVE_COMPARATOR": "CHECK_MISREADS_HELD_ROWS", "CONTROL_CODED_AS_ACTIVE": "CHECK_MISREADS_HELD_ROWS",
          "LEXICON_GAP": "CHECK_MISREADS_HELD_ROWS", "WILDCARD_NOT_HONOURED": "CHECK_MISREADS_HELD_ROWS",
          "TERM_FORM_MISMATCH": "CHECK_MISREADS_HELD_ROWS", "NON_CTGOV_REGISTRY": "CHECK_CANNOT_READ_SOURCE",
          "NO_REGISTRY_PARENT_LINKED": "CHECK_CANNOT_READ_SOURCE", "CONDITIONS_TOO_GENERAL": "NOT_ESTABLISHED_IN_ROWS",
          "CONDITIONS_DIFFER": "NOT_ESTABLISHED_IN_ROWS", "NOT_DERIVABLE_FROM_ARMS": "NOT_ESTABLISHED_IN_ROWS",
          "INELIGIBLE_ON_HELD_EVIDENCE": "INELIGIBLE_ON_HELD_ROWS"}
PROVEN = {"NCT03030235", "NCT01897532", "NCT02422186", "NCT03334604", "NCT00403767", "NCT00391872", "NCT01035255"}

per = collections.defaultdict(list)
for m, s in zip(mine, sub):
    per[m["audit_id"]].append({
        "trial_id": m["trial"], "family_id": m["family"], "gate_code": m["code"] or m["label"],
        "class": m["lane_class"], "bucket": BUCKET[m["lane_class"]], "basis": m["lane_basis"]
        + (" [shown by executing harness.trial_family.screen_family with only this field changed: the family "
           "becomes ELIGIBLE]" if m["family"] in PROVEN else ""),
        "second_reader_class": s["class"], "second_reader_bucket": BUCKET[s["class"]]})

out = []
for v in b1["verdicts"]:
    v = dict(v)
    binding = per.get(v["audit_id"], [])
    misread = sum(b["bucket"] == "CHECK_MISREADS_HELD_ROWS" for b in binding)
    agreed = sum(b["bucket"] == "CHECK_MISREADS_HELD_ROWS" == b["second_reader_bucket"] for b in binding)
    if binding and misread == len(binding):
        lead = (f"B2: EVERY departure ({misread} of {len(binding)}; second reader agrees on {agreed}) fails the admission "
                "check because of how the check reads rows the site already holds, not because the evidence is "
                "absent. The notice records accurately what the gate did, but countersigning it ratifies a "
                "served-number change the check produced. The lane recommends fixing the check and regenerating the "
                "notice before signing. That is a recommendation, not a decision.")
    elif misread:
        lead = (f"B2: {misread} of {len(binding)} departures (second reader agrees on {agreed}) fail the admission "
                "check because of how it reads held rows; the rest rest on evidence the check cannot read or that is "
                "not established in the rows (per trial below).")
    elif binding:
        lead = (f"B2: none of the {len(binding)} departures is a misread of held rows; per trial below (check cannot "
                "read the source, or the rows do not establish the population).")
    else:
        lead = "B2: no departing trial."
    v["lane_notes"] = lead + ((" " + v["lane_notes"]) if v.get("lane_notes") else "")
    v["departure_binding"] = binding
    v["second_reader"] = ("Claude subagent a41079929466ae7a5 (same model family as the lane; blind to the lane's "
                          "labels); codex NR-C02 on the same packet hit its usage limit (rc=1, logged)")
    out.append(v)
Path(WORK / "verdicts_b2.json").write_bytes(
    json.dumps({"served": b1["served"], "proposed": b1["proposed"], "verdicts": out}, ensure_ascii=False, indent=1).encode())
print(collections.Counter(v["lane_notes"][:40] for v in out))
