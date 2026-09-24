"""evidence/p5_populations/REPORT.md -- every count computed from ledger.json and ev53_reverify.json."""
import collections, json, os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
L = json.load(open(os.path.join(BASE, "ledger.json"), encoding="utf-8"))
RV = json.load(open(os.path.join(BASE, "ev53_reverify.json"), encoding="utf-8"))
rows = L["rows"]
assert len(rows) == 53
out = ["# The 53 P5-unestablished pooled rows -- population evidence under POLICY.md", "",
       "Kinds of item: 53 served pooled primary rows (the frozen `evidence/inputs/the53.json`), each carrying the facts of "
       f"its ordered P5 blocker chain ({L['N_facts']} facts). No controls, no split rows. No row is omitted; a row whose "
       "facts are UNRESOLVED stays in the population with its served value.", "",
       "## Rows (of 53)", ""]
for k, v in sorted(collections.Counter(r["row_state"] for r in rows).items()):
    out.append(f"- {k}: **{v} of 53**")
out += ["", f"## Facts (of {L['N_facts']})", ""]
for k, v in sorted(L["fact_states"].items()):
    out.append(f"- {k}: {v}")
out += ["", "By fact:", ""] + [f"- `{k}`: " + ", ".join(f"{s} {n}" for s, n in sorted(v.items())) for k, v in L["by_fact"].items()]
out += ["", "## The predecessor's citations, re-checked", "",
        f"All {RV['N']} EV53 citations re-located by evid2 at checkout `{RV['checkout'][:8]}`: " +
        ", ".join(f"{k} {v}" for k, v in sorted(RV["tally"].items())) +
        ". The one EMPTY_SPAN was labelled a pass by EV53 (an empty string is trivially found); no fact cites it.", "",
        "## Every fact that is not RECOVERED", "", "| row | trial | fact | state | why |", "|---|---|---|---|---|"]
for r in rows:
    for f in r["facts"]:
        if f["state"] != "RECOVERED":
            out.append(f"| {r['key']} | {r['trial']} ({r['slug']}) | {f['fact_id']} | {f['state']} | "
                       f"{(f['basis'] or '').replace('|', '/')[:300]} |")
out += ["", "## Recovered, with a note a reader must see", ""]
for r in rows:
    for f in r["facts"]:
        if f["state"] == "RECOVERED" and f["notes"]:
            out.append(f"- {r['key']} {r['trial']} `{f['fact_id']}`: " + "; ".join(f["notes"]))
h = [r for r in rows if r["trial"] == "PMID 30291013"][0]
out += ["", "## HARMONY", "",
        f"{h['key']} ({h['slug']}, family {h['family_id']}): P5 blocker `{h['p5_absence_code']}`, row state "
        f"**{h['row_state']}**. " + " ".join(f"`{f['fact_id']}` {f['state']}: \"{f['evidence'][0]['span'][:220]}\"" for f in h["facts"] if f["evidence"]), "",
        "## What this is not", "",
        "- RECOVERED is evidence for Mahmood's decision D04. It admits no row; no admission route was created or used.",
        "- The P5 screen reads registry conditions; a fact recovered from a report does not turn the screen green, and "
        "the probiotics rows additionally carry a config defect (the configured population terms name the outcome).",
        "- UNRESOLVED means the stopping rule of POLICY.md was reached without a span -- not that the fact is false."]
open(os.path.join(BASE, "REPORT.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("ok")
