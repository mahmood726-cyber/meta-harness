"""REVIEW_SHEET.md for the human reviewer: every RoB 2 domain PROPOSAL for the GLP-1 3-point MACE result, with its reason,
its witness sources (kind + file; the verbatim spans are in the per-trial JSON), and an EMPTY reviewer line. Derived
from the per-trial files; nothing here finalises anything.
  python evidence/rob2_glp1/make_review_sheet.py"""
import glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DOM = {"D1_randomisation": "D1 randomisation", "D2_deviations_assignment": "D2 deviations (assignment)",
       "D3_missing_outcome_data": "D3 missing outcome data", "D4_outcome_measurement": "D4 outcome measurement",
       "D5_selection_of_reported_result": "D5 selection of reported result"}


def main():
    s = json.load(open(os.path.join(HERE, "SUMMARY.json"), encoding="utf-8"))
    L = ["# RoB 2 (outcome-specific) -- GLP-1 RA 3-point MACE: PROPOSALS awaiting human review", "",
         f"**Status: every judgement below is a PROPOSAL (`{s['status']}`). None is final; the reviewer line is empty on purpose.**",
         f"Result assessed: 3-point MACE hazard ratio, effect of assignment (ITT). Domains with held evidence: "
         f"**{s['domains_with_evidence']} of {s['population']['N_domains']}** ({s['population']['denominator']}).",
         "Proposals: " + ", ".join(f"{k} {v}" for k, v in sorted(s["proposals"].items())) + ". "
         "`NO_EVIDENCE_HELD` means no held source speaks to the domain -- it is NOT a risk level and is never relabelled high.",
         "Stopped treatment is recorded separately (D2 context) and never used as missing outcome data (D3). "
         "A registry entry alone is never taken as proof of prespecification (D5).", ""]
    for p in sorted(glob.glob(os.path.join(HERE, "*.json"))):
        if os.path.basename(p) in ("SPEC.json", "SUMMARY.json"):
            continue
        d = json.load(open(p, encoding="utf-8"))
        L += [f"## {d['trial']} (PMID {d['pmid']}, {d['nct']}) -- overall proposal: {d['overall']['proposal']}", "",
              "| domain | proposal | why | witness sources | reviewer decision |", "|---|---|---|---|---|"]
        for k, name in DOM.items():
            v = d["domains"][k]
            src = "; ".join(f"{w['source_kind']}: `{w['ref'].split('/')[-2]}/{w['ref'].split('/')[-1]}`" for w in v["witnesses"]) or "--"
            L.append(f"| {name} | **{v['proposal']}** | {v['why'].replace('|', '/')} | {src} | ______ |")
        td = d.get("D2_treatment_discontinuation")
        if td:
            L.append(f"\nStopped treatment (D2 context, not missing data): {td['why']}")
        L.append("")
    open(os.path.join(HERE, "REVIEW_SHEET.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("REVIEW_SHEET.md written")


if __name__ == "__main__":
    main()
