"""Register addendum from ACCEPTED decisions only, grouped by class, register columns. Codex outputs supply title and proposed
fixture; the decision note (this lane's hostile review) supplies the defect wording."""
import json
from collections import defaultdict

L = [json.loads(l) for l in open("decisions.jsonl", encoding="utf-8")]
out = {s: json.load(open(f"out/{s}.json", encoding="utf-8")) for s in {d["topic"] for d in L}}
calls = [json.loads(l) for l in open("calls.jsonl", encoding="utf-8")]
SERVED_NUMBER = {("spironolactone-hfref-mortality", 0), ("empagliflozin-hfpef-hosp", 0), ("semaglutide-obesity-weight", 0)}
SERVED_TEXT = {("noac-vs-warfarin-af-stroke", 0), ("semaglutide-obesity-mace", 0), ("statins-primary-prevention-elderly", 0),
               ("statins-primary-prevention-elderly", 2), ("statins-primary-prevention-elderly", 4), ("sglt2-primary-prevention-hf", 1)}
NAMES = {"C1": "Held-text blind spots -- served 'absent / not stated' contradicted by held text",
         "C2": "Effect-measure identity", "C3": "Endpoint relations and polarity", "C4": "Population witness (screening reasons)",
         "C5": "Report / family / version linkage", "C6": "Comparator records", "C7": "Auditor identity matching / adjudication",
         "C8": "Labels, narrative and metadata field-links"}
by = defaultdict(list)
for d in L:
    by[d["class"]].append(d)
lines = ["# V1.0.1 findings register -- ADDENDUM from the pva internal topic audit (27 Sep 2026)", "",
         "**For the release captain to merge into F:/mh-gate/outputs/V1_0_1_FINDINGS_REGISTER.md (this lane does not edit that file).**", "",
         f"- Scope: the **22** served topics the external reviewer has not covered; **22 of 22 audited** on V1 = main 9eacfe09.",
         f"- Engine: codex exec (GPT-6, read-only sandbox) on a read-only 808-file extract; one job per topic; {len(calls)} logged calls "
         f"(prompt sha256, rc, tokens, output sha256 in calls.jsonl); total tokens {sum(int((c['tokens'] or '0').replace(',', '')) for c in calls):,}.",
         "- Gate 1 (machine): every quoted span must exist in the named held file (proven: a fabricated sentence, a one-digit change "
         "and a wrong file are all rejected). 120 of 122 passed; the 2 failures were cosmetic misquotes of real held text "
         "(Lancet middle dot; a lower-case sentence start) and were re-verified against the exact held bytes (amendments.json).",
         "- Gate 2 (machine): the served claim must sit in a JSON object naming the finding's trial (identity.json); ambiguous ones checked by hand.",
         "- Gate 3 (this lane): hostile review of every finding; value checks on every consequential one. **122 of 122 accepted: "
         f"{sum(d['decision'] == 'ACCEPT' for d in L)} as written, {sum(d['decision'] == 'ACCEPT_AMENDED' for d in L)} narrowed or "
         f"corrected, {sum(d['decision'] == 'ACCEPT_RECLASSIFIED' for d in L)} moved to another class; 0 rejected outright.** "
         "Two codex claims were NOT accepted in full and are narrowed below (VESALIUS refusal; CONFIRM-HF 'severe' allergy).",
         "- `served` column: **NUMBER** = a served number changes when fixed (needs a signed notice); **TEXT** = served page wording is false; "
         "blank = a field/audit defect not rendered as a number.", "",
         "| class | findings | topics |", "|---|---|---|"]
for c in sorted(by):
    lines.append(f"| {c} {NAMES[c]} | {len(by[c])} | {len({d['topic'] for d in by[c]})} |")
lines.append(f"| **total** | **{len(L)}** | **{len({d['topic'] for d in L})}** |")
for c in sorted(by):
    lines += ["", f"## {c} -- {NAMES[c]}", "",
              "| id | topic | defect (hostile-reviewed) | served | proposed fixture (codex; plant must fire pre-fix) | state |",
              "|---|---|---|---|---|---|"]
    for i, d in enumerate(sorted(by[c], key=lambda x: (x["topic"], x["n"])), 1):
        f = out[d["topic"]]["findings"][d["n"]]
        key = (d["topic"], d["n"])
        served = "**NUMBER**" if key in SERVED_NUMBER else ("TEXT" if key in SERVED_TEXT else "")
        tag = "" if d["decision"] == "ACCEPT" else f" _({d['decision'].lower().replace('_', ' ')})_"
        fx = f["proposed_fixture"].replace("|", "\\|").replace("\n", " ")[:260]
        lines.append(f"| {c}.pva{i} | {d['topic']} | {d['note'].replace('|', '/')}{tag} | {served} | {fx} | NOT STARTED |")
lines += ["", "## Served-number items (need a signed notice when fixed)",
          "- **spironolactone-hfref-mortality**: the PRIMARY all-cause-mortality pool (k 3, HR 0.7294) includes J-EMPHASIS-HF's "
          "CV-death-or-HF-hospitalisation composite HR 0.85.",
          "- **empagliflozin-hfpef-hosp**: the PRIMARY composite is served with no pooled result; EMPEROR-Preserved's held abstract has "
          "the counts and HR 0.79 (0.69-0.90).",
          "- **semaglutide-obesity-weight**: STEP 1 and STEP 3 means/SDs are paired with all-randomised denominators instead of the "
          "measured n; the pooled SEs move.",
          "", "## Relation to the source-preservation census (same day)",
          "The census over all 3,330 held PubMed records found 2 abridged abstracts (OMNeON in dpp4, SOUL in glp1). In these 22 topics "
          "only SOUL applies; codex was told the census result and found no further abridgement. See SOURCE_CENSUS_2026-09-27.md."]
open("REGISTER_ADDENDUM_pva_2026-09-27.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(len(lines), "lines")
