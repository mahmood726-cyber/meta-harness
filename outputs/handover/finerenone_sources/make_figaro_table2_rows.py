"""FIGARO-DKD (PMID 34449181) hyperkalaemia rows from its Table 2 'Safety Outcomes', 2026-09-27.

Held: the accepted manuscript (curis.ku.dk repository copy via Unpaywall, licence other-oa; local only, not
redistributed), sha256 recorded in HELD.json. Committed: a TABLES excerpt of Table 2 (header with the arm sizes, the
two rows), every cell asserted in our own pypdf page text of the held PDF.
  Hyperkalemia (footnote: investigator-reported MedDRA 'hyperkalemia' + 'blood potassium increased'): 396/3683 vs 193/3658
  Permanent discontinuation of trial regimen due to hyperkalemia: 46/3683 vs 13/3658
Safety population: patients who received at least one dose. The previous typed refusals (abstract percentages only;
AACT splits serious/non-serious terms) are kept as `supersedes`. FIDELIO-DKD's Table 2 is NOT openly held (NEJM and its
repository copy answer 403): it stays REPORTED_UNRESOLVED.
  PYTHONPATH=. python outputs/handover/finerenone_sources/make_figaro_table2_rows.py"""
import hashlib, json, os, re

import pypdf

PDF = "evidence/acquisition_cascade/held/PMID34449181/unpaywall.pdf"
EX = "evidence/acquisition_cascade/excerpts/FIGARO_Table2_safety.tables.txt"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
led = json.load(open("evidence/acquisition_cascade/held/HELD.json", encoding="utf-8"))
assert led["PMID34449181/unpaywall.pdf"]["sha256"] == sha(PDF)

page = re.sub(r"\s+", " ", pypdf.PdfReader(PDF).pages[10].extract_text() or "")
for cell in ("Table 2. Safety Outcomes.", "Finerenone (N = 3683)", "Placebo (N = 3658)", "Hyperkalemia† 396 (10.8) 193 (5.3)",
             "Permanent discontinuation of trial regimen due to hyperkalemia 46 (1.2) 13 (0.4)",
             "reported by investigators with the use of the Medical Dictionary for Regulatory Activities (MedDRA) preferred terms",
             "received at least one dose of finerenone or placebo"):
    assert cell in page, cell

HYPER = "Hyperkalemia† | 396 (10.8) | 193 (5.3)"
DISC = "Permanent discontinuation of trial regimen due to hyperkalemia | 46 (1.2) | 13 (0.4)"
os.makedirs(os.path.dirname(EX), exist_ok=True)
open(EX, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of FIGARO-DKD Table 2 'Safety Outcomes' (Pitt et al., NEJM 2021; accepted manuscript, curis.ku.dk, "
    "licence other-oa, held locally, not redistributed). Every value is verbatim from our pypdf text of the held PDF, page 11; "
    "the CELL BOUNDARIES are this excerpt's segmentation of that text run.\n"
    f"# held PDF: {PDF} sha256 {sha(PDF)}\n"
    "# footnote † (verbatim): Shown are adverse events that were reported by investigators with the use of the Medical "
    "Dictionary for Regulatory Activities (MedDRA) preferred terms \"hyperkalemia\" and \"blood potassium increased.\"\n"
    "# population (verbatim): patients who received at least one dose of finerenone or placebo\n\n"
    "=== TABLES (excerpt) ===\n"
    "TABLE Table 2. Safety Outcomes.\n"
    "Event | Finerenone (N = 3683) | Placebo (N = 3658)\n"
    + HYPER + "\n" + DISC + "\n")

SAFETY = "safety population: patients who received at least one dose (3683 finerenone vs 3658 placebo)"
vp = "cache/finerenone-ckd-t2d-renal/verified_arms.json"
va = json.load(open(vp, encoding="utf-8")) if os.path.exists(vp) else {}
vep = "cache/finerenone-ckd-t2d-renal/verified_effects.json"
raw_e = open(vep, encoding="utf-8").read()
ve = json.loads(raw_e)
old = {r["outcome"]: r for r in ve["34449181"]}
rows = []
for outcome, span, a, c in (("Hyperkalemia", HYPER, 396, 193),
                            ("Hyperkalemia-related treatment discontinuation", DISC, 46, 13)):
    rows.append({"outcome": outcome, "ai": a, "n1i": 3683, "ci": c, "n2i": 3658, "kind": "extracted_counts",
                 "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
                 "document_ref": EX, "document_sha256": sha(EX), "source_span": span, "safety_population": SAFETY,
                 "supersedes": {k: old[outcome].get(k) for k in ("provenance", "reason") if old[outcome].get(k)},
                 "reason": (f"FIGARO-DKD {outcome.lower()} from Table 2 of the trial's own report (accepted manuscript, "
                            f"held locally; committed as a TABLES excerpt): {a}/3683 vs {c}/3658, {SAFETY}.")})
va["34449181"] = rows
open(vp, "w", encoding="utf-8", newline="\n").write(json.dumps(va, indent=2, ensure_ascii=False) + "\n")
ve["34449181"] = [r for r in ve["34449181"] if r["outcome"] not in ("Hyperkalemia", "Hyperkalemia-related treatment discontinuation")]
# FIDELIO-DKD: its Table 2 is not openly held. Its rows REPORT the outcome, so they carry the verbatim evidence of that
# on the row itself (state REPORTED_UNRESOLVED however other trials pool; it used to depend on the outcome having no
# pooled result at all, and pooling FIGARO turned it into 'retrieved, not reported')
fid_abs = next(x for x in json.load(open("cache/finerenone-ckd-t2d-renal/records.json", encoding="utf-8"))["records"]
               if str(x["id"]) == "33264825")["abstract"]
FID_DISC = ("The incidence of hyperkalemia-related discontinuation of the trial regimen was higher with finerenone than "
            "with placebo (2.3% and 0.9%, respectively).")
assert FID_DISC in fid_abs
FID_REG = "evidence/acquisition_cascade/held/PMID33264825/NCT02540993.json"
reg = json.load(open(FID_REG, encoding="utf-8"))["resultsSection"]["adverseEventsModule"]
hk = [e for e in reg["seriousEvents"] + reg["otherEvents"] if e["term"] == "Hyperkalaemia"]
assert len(hk) == 2
for r in ve["33264825"]:
    if r["outcome"] == "Hyperkalemia-related treatment discontinuation":
        r["reported_unresolved_span"] = FID_DISC
    elif r["outcome"] == "Hyperkalemia":
        r["reported_unresolved_span"] = "Hyperkalaemia"
        r["reported_unresolved_source"] = {"path": FID_REG, "sha256": sha(FID_REG), "what": (
            "the trial's posted registry adverse events list the MedDRA term 'Hyperkalaemia' as serious (42/2827 vs "
            "12/2831) and non-serious (422/2827 vs 212/2831) rows; a participant may be in both, so they cannot be summed "
            "into the participant count its Table 2 reports (Table 2 not openly held: NEJM and its repository copy 403)")}
open(vep, "w", encoding="utf-8", newline="\n").write(json.dumps(ve, indent=2, ensure_ascii=False) + ("\n" if raw_e.endswith("\n") else ""))

# the source's own words for the discontinuation outcome (Table 2), added as a keyword of THAT outcome only
tp = "topics/finerenone-ckd-t2d-renal.json"
raw_t = open(tp, encoding="utf-8").read()
cfg = json.loads(raw_t)
spec = next(s for s in cfg["harm_outcomes"] if s["name"] == "Hyperkalemia-related treatment discontinuation")
kw = "discontinuation of trial regimen due to hyperkalemia"
if kw not in spec["keywords"]:
    spec["keywords"].append(kw)
open(tp, "w", encoding="utf-8", newline="\n").write(json.dumps(cfg, indent=2, ensure_ascii=False) + ("\n" if raw_t.endswith("\n") else ""))
print("FIGARO Table 2: 2 rows bound; excerpt", EX)
