"""Statins-older-adults (statins-primary-prevention-elderly) fixtures, 2026-09-28. Every span is asserted against held bytes.
 (1) INVESTIGATOR SUBGROUP REPORT: Ridker 2017 (Circulation research letter, PMID 28385949) reports new >=70 analyses of
     JUPITER and HOPE-3 and pools them. Only its Europe PMC record is held (no abstract; not open; unpaywall: no open
     copy), so its values are RELAYED, never admitted: HOPE-3 >=70 3-point MACE HR 0.83 (0.64-1.07) (HOPE-3,
     NCT00468923, absent from the inventory: registration held -- a 2x2 FACTORIAL); JUPITER >=70 3-point MACE 0.61
     (0.43-0.86), a DIFFERENT outcome record from the served broader JUPITER composite 0.61 (0.46-0.82) -- both kept.
     The letter's pooled JUPITER+HOPE-3 estimate is a combined analysis: NEVER_IMPORTED (docs/multi_trial_reports.json).
 (2) ALLHAT-LLT: Han 2017 (PMID 28531241) and Orkaby 2018 (PMID 30251369, RMST) report the SAME trial (NCT00000542,
     2,867; 1,467 vs 1,400): one family; RMST differences are never HRs. Its >=75 fatal CHD/nonfatal MI HR 0.70
     (0.43-1.13) is a coronary outcome without stroke -- not 'major vascular events' -- and ALL-CAUSE mortality 1.34
     (0.98-1.84) is a separate outcome this review does not carry; its >=65 analysis is not the >=70 target. 'Specific
     adverse effects data were not collected' -> NOT_SYSTEMATICALLY_COLLECTED for both harms.
 (3) JUPITER >=70 Table 3 (held PMC page, NIH manuscript): muscle weakness/stiffness/pain 494 vs 467, HR 1.04 (0.92-1.19);
     myopathy 4 vs 3, 1.31 (0.29-5.84); newly diagnosed diabetes 82 vs 64, 1.25 (0.90-1.74) -- kept as HRs; muscle
     symptoms and myopathy are separate rows, never summed.
 (4) STAREE safety supplement: not retrievable by open routes (NEJM; Europe PMC not open; unpaywall no location).
  PYTHONPATH=. python outputs/handover/statins_sources/make_statins_fixtures.py"""
import hashlib, json, os, re

SLUG = "statins-primary-prevention-elderly"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
REC = f"cache/{SLUG}/records.json"
BY = "evidence lane (Claude Opus 5.5), 2026-09-28, source-backed"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
MVE, MUS, DM = "Major vascular events", "Muscle symptoms/myopathy", "New-onset diabetes"
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"[\[{]\n( +)", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


def held(path, span, where):
    n = flat(open(path, encoding="utf-8").read()).count(flat(span))
    assert n >= 1, f"{where}: {span!r} not in {path}"
    return span


# ------------------------------------------------------------------ (3) JUPITER >=70 Table 3 (held PMC page; local text)
J_HTML, J_TXT = f"{H}/JUPITER-older/pmc_article.html", f"{H}/JUPITER-older/pmc_article.local.txt"
JT = flat(open(J_TXT, encoding="utf-8").read())
J_CAP = "Table 3. Monitored adverse events and other events of interest by age and treatment group"
J_MUS = "Muscle weakness, stiffness or pain 494 8.92 467 8.50 1.04 (0.92–1.19)"
J_MYO = "Myopathy 4 0.06 3 0.05 1.31 (0.29–5.84)"
J_DM = "Newly diagnosed diabetes 82 1.30 64 1.03 1.25 (0.90–1.74)"
J_FN = "† Hazard ratios compare hazards in the rosuvastatin group to placebo"
J_AGE = "Age 70–97 years Age 50–69 years"
for s in (J_CAP, J_MUS, J_MYO, J_DM, J_CAP + " " + J_AGE):   # the age header anchored to THIS table's caption
    assert JT.count(s) == 1, s
assert JT.count(J_FN) >= 1, J_FN   # the footnote is repeated under each table
J_EXC = f"{X}/JUPITER-older_Table3.tables.txt"
open(J_EXC, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of JUPITER >=70 (Glynn et al., Ann Intern Med 2010) Table 3, PMC2946369 page (NIH author manuscript, free to "
    "read); held locally, not redistributed. Every value is verbatim from our text of the held page; the CELL BOUNDARIES "
    "are this excerpt's segmentation. Only the 'Age 70–97 years' columns are excerpted; the 50–69 columns are never "
    "this review's population. Rates are per 100 person-years; hazard ratios compare rosuvastatin with placebo.\n"
    f"# held: {J_HTML} sha256 {sha(J_HTML)}\n\n"
    "=== TABLES (excerpt) ===\n"
    f"TABLE {J_CAP} (Age 70–97 years)\n"
    "Monitored adverse event | Rosuvastatin N | Rosuvastatin rate | Placebo N | Placebo rate | Hazard ratio (95% CI)\n"
    "Muscle weakness, stiffness or pain | 494 | 8.92 | 467 | 8.50 | 1.04 (0.92–1.19)\n"
    "Myopathy | 4 | 0.06 | 3 | 0.05 | 1.31 (0.29–5.84)\n"
    "Newly diagnosed diabetes | 82 | 1.30 | 64 | 1.03 | 1.25 (0.90–1.74)\n")
R_MUS = "Muscle weakness, stiffness or pain | 494 | 8.92 | 467 | 8.50 | 1.04 (0.92–1.19)"
R_DM = "Newly diagnosed diabetes | 82 | 1.30 | 64 | 1.03 | 1.25 (0.90–1.74)"

# ------------------------------------------------------------------ (2) ALLHAT-LLT Table 2 + collection rule (held PMC page)
A_HTML, A_TXT = f"{H}/ALLHAT-LLT-older/pmc_article.html", f"{H}/ALLHAT-LLT-older/pmc_article.local.txt"
AT = flat(open(A_TXT, encoding="utf-8").read())
A_CAP = ("Table 2. Six-Year Incidence Rates for Primary and Secondary Outcomes in the ALLHAT-LLT, Cumulative Events, and "
         "Relative Risks Based on the Entire Follow-up by Age Group.")
A_CHD = "Fatal CHD and nonfatal MI a 107 128 8.8 (0.9) 11.3 (1.0) 0.81 (0.63-1.05) .12 65-74 y 76 89 8.4 (1.1) 10.2 (1.1) 0.85 (0.62-1.15) .29 ≥75 y 31 39 9.9 (1.9) 14.9 (2.7) 0.70 (0.43-1.13) .14"
A_ACM = "All-cause mortality 233 195 19.4 (1.3) 16.2 (1.2) 1.18 (0.97-1.42) .09 65-74 y 141 130 15.5 (1.3) 14.2 (1.3) 1.08 (0.85-1.37) .55 ≥75 y 92 65 31.0 (3.2) 22.7 (3.0) 1.34 (0.98-1.84) .07"
A_AE = "Specific adverse effects data were not collected."
A_POSTHOC = "Post hoc secondary data analyses were conducted of participants 65 years and older"
for s in (A_CAP, A_CHD, A_ACM, A_AE, A_POSTHOC):
    assert AT.count(s) >= 1, s
A_EXC = f"{X}/ALLHAT-LLT-older_Table2_collection.tables.txt"
open(A_EXC, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of ALLHAT-LLT older adults (Han et al., JAMA Intern Med 2017) Table 2 and one methods sentence, PMC5543335 "
    "page (NIH author manuscript, free to read); held locally, not redistributed. Every value is verbatim from our text of "
    "the held page; the CELL BOUNDARIES are this excerpt's segmentation. Pravastatin vs USUAL CARE (open label).\n"
    f"# held: {A_HTML} sha256 {sha(A_HTML)}\n\n"
    f"{A_POSTHOC} without evidence of atherosclerotic cardiovascular disease. {A_AE}\n\n"
    "=== TABLES (excerpt) ===\n"
    f"TABLE {A_CAP}\n"
    "Outcome | Pravastatin cumulative events | Usual care cumulative events | Pravastatin 6-y rate (SE) | Usual care 6-y rate (SE) | HR (95% CI) | P value\n"
    "Fatal CHD and nonfatal MI, ≥75 y | 31 | 39 | 9.9 (1.9) | 14.9 (2.7) | 0.70 (0.43-1.13) | .14\n"
    "All-cause mortality, ≥75 y | 92 | 65 | 31.0 (3.2) | 22.7 (3.0) | 1.34 (0.98-1.84) | .07\n")
assert AT.count(flat(A_POSTHOC + " without evidence of atherosclerotic cardiovascular disease")) >= 1
R_CHD = "Fatal CHD and nonfatal MI, ≥75 y | 31 | 39 | 9.9 (1.9) | 14.9 (2.7) | 0.70 (0.43-1.13) | .14"

# ------------------------------------------------------------------ hand entries
ve_p = f"cache/{SLUG}/verified_effects.json"
ve = json.load(open(ve_p, encoding="utf-8"))
JUP, ALL, ORK = "20404379", "28531241", "30251369"
ju = [r for r in as_list(ve.get(JUP)) if r.get("outcome") not in (MUS, DM)]
ju += [
    {"outcome": MUS, "override": True, "effect": 1.04, "ci_low": 0.92, "ci_high": 1.19, "scale": "HR",
     "provenance": "fulltext_verified", "source_level": 1, "document_ref": J_EXC, "document_sha256": sha(J_EXC),
     "source_span": R_MUS, "harm_definition": "muscle weakness, stiffness or pain (monitored adverse event)",
     "harm_definition_key": "MUSCLE_SYMPTOMS",
     "source": (f"{J_EXC}: JUPITER Table 3, age 70-97, muscle weakness, stiffness or pain 494 vs 467, HR 1.04 "
                "(0.92-1.19). MYOPATHY (4 vs 3, HR 1.31, 0.29-5.84) is a separate row, never summed into it.")},
    {"outcome": DM, "override": True, "effect": 1.25, "ci_low": 0.90, "ci_high": 1.74, "scale": "HR",
     "provenance": "fulltext_verified", "source_level": 1, "document_ref": J_EXC, "document_sha256": sha(J_EXC),
     "source_span": R_DM, "harm_definition": "newly diagnosed diabetes", "harm_definition_key": "INCIDENT_DIABETES",
     "source": f"{J_EXC}: JUPITER Table 3, age 70-97, newly diagnosed diabetes 82 vs 64, HR 1.25 (0.90-1.74)"}]
ve[JUP] = ju
al = [r for r in as_list(ve.get(ALL)) if r.get("outcome") != MVE]
al.append({"outcome": MVE, "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE", "override": True,
           "source_level": 1, "document_ref": A_EXC, "document_sha256": sha(A_EXC), "source_span": R_CHD,
           "held_out_row": {"effect": 0.70, "ci_low": 0.43, "ci_high": 1.13, "scale": "HR"},
           "not_admitted_because": ("fatal CHD or nonfatal MI in adults >= 75: a CORONARY outcome without stroke, not major "
                                    "vascular events; the >= 65 analysis is not this review's >= 70 target"),
           "reason": ("ALLHAT-LLT (pravastatin vs usual care; post hoc older-adult analysis) reports no major-vascular-events "
                      "outcome: its >= 75 fatal CHD or nonfatal MI HR 0.70 (0.43-1.13) is a coronary outcome without "
                      "stroke, and its >= 75 ALL-CAUSE mortality HR 1.34 (0.98-1.84) is a separate outcome this review does "
                      "not carry. Neither is substituted; the >= 65 analysis is not the >= 70 target.")})
ve[ALL] = al
dump(ve_p, ve)

# ------------------------------------------------------------------ ALLHAT: specific adverse effects NOT collected
cp = "docs/collection_scope.json"
cs = json.load(open(cp, encoding="utf-8"))
cs["topics"][SLUG] = [{
    "trial": f"PMID {ALL}", "outcome": o,
    "collected": "outcome events (mortality, CHD, stroke, heart failure, cancer); reasons for stopping pravastatin",
    "not_collected": "specific adverse effects",
    "why": "the report states that specific adverse-effect data were not collected: no count of this outcome exists, "
           "never 'not reported' and never zero",
    "collection_rule_witnesses": [W(A_EXC, A_AE)]} for o in (MUS, DM)]
dump(cp, cs)

# ALLHAT: one family -- Orkaby 2018 (RMST) is linked to Han 2017 by harness/report_linkage.py from its own text
# ('Secondary analysis of ... (ALLHAT-LLT)' + shared arm sizes 1,467/1,400); nothing is declared here.

# ------------------------------------------------------------------ (1) Ridker 2017: a multi-trial report, never an input
R_REC = f"{H}/Ridker-2017-JUPITER-HOPE3-older/europepmc_record_28385949.json"
R_TITLE = held(R_REC, "Primary Prevention With Statin Therapy in the Elderly: New Meta-Analyses From the Contemporary JUPITER "
                      "and HOPE-3 Randomized Trials.", "Ridker title")
HREG = f"{H}/HOPE-3-registration/NCT00468923.json"
hj = json.load(open(HREG, encoding="utf-8"))["protocolSection"]
assert hj["designModule"]["designInfo"]["interventionModel"] == "FACTORIAL"
H_EXCL = held(HREG, "Documented clinically manifest atherothrombotic CVD", "HOPE-3 exclusion")
H_TITLE = held(HREG, "Heart Outcomes Prevention Evaluation-3", "HOPE-3 title")
J_POP = held(J_TXT, "with no history of cardiovascular disease or diabetes", "JUPITER population")
J_AGE70 = held(REC, "5695 were 70 years or older", "JUPITER >=70 n")
mp = "docs/multi_trial_reports.json"
md = json.load(open(mp, encoding="utf-8"))
md["reports"] = [r for r in md["reports"] if r.get("report_id") != "PMID 28385949"] + [{
    "report_id": "PMID 28385949",
    "citation": "Ridker PM et al. Circulation 2017 (research letter): new >=70 meta-analyses of JUPITER and HOPE-3",
    "kind": "INVESTIGATOR_SUBGROUP_REPORT_WITH_POOLED_ANALYSIS",
    "trials": [
        {"label": "JUPITER (>= 70)", "registration": f"PMID:{JUP}", "reports": [f"PMID {JUP}"],
         "population": {"witness": W(REC, J_AGE70)}},
        # the >= 70 SUBGROUP's population is the report's (its title: 'Primary Prevention ... in the Elderly'); the
        # registry's own criteria (no manifest CVD) are witnessed alongside
        {"label": "HOPE-3 (>= 70)", "registration": "NCT00468923", "reports": [],
         "population": {"witness": W(R_REC, R_TITLE)}, "registration_witness": W(HREG, H_TITLE),
         "registry_population_witness": W(HREG, H_EXCL)}],
    "combined_analyses": [{"label": "JUPITER + HOPE-3 >= 70 pooled estimate", "policy": "NEVER_IMPORTED",
                           "witness": W(R_REC, R_TITLE)}],
    "full_text_state": ("NOT HELD: Europe PMC record only (a letter: no abstract; not open access); unpaywall: no open "
                        "location. Its per-trial >=70 values are RELAYED (docs/known_eligible_missing.json, "
                        "docs/relayed_values.json), never admitted")}]
dump(mp, md)

# ------------------------------------------------------------------ HOPE-3: known eligible, absent from the inventory
kp = "docs/known_eligible_missing.json"
kd = json.load(open(kp, encoding="utf-8"))
kd["topics"][SLUG] = [e for e in kd["topics"].get(SLUG) or [] if e.get("registration") != "NCT00468923"] + [{
    "trial": "HOPE-3", "registration": "NCT00468923", "pmid": None,
    "mechanism": ("inventory (absent from the committed search snapshot); its >= 70 statin-vs-placebo analysis exists only in "
                  "an investigator subgroup report (Ridker 2017, PMID 28385949) that is not held"),
    "status": "report_not_held",
    "acquisition": {"route": ("acquisition cascade: ClinicalTrials.gov registration (held; no posted results); Ridker 2017 "
                              "Europe PMC record held (a letter, no abstract; not open access; unpaywall no location)"),
                    "registration_path": HREG, "registration_sha256": sha(HREG),
                    "record_path": R_REC, "record_sha256": sha(R_REC)},
    "design": ("randomised, double-blind (registry masking QUADRUPLE), 2x2 FACTORIAL: rosuvastatin vs placebo crossed with "
               "candesartan/hydrochlorothiazide vs placebo; intermediate-risk people without cardiovascular disease"),
    "design_note": ("RELAYED (not data; the report is not held): HOPE-3 >= 70 (n=3,086) 3-point MACE HR 0.83 (0.64-1.07). A "
                    "post hoc age subgroup of a FACTORIAL trial (the statin comparison is the rosuvastatin factor). "
                    "Diagnostic only (relayed): the 3-input pool with it would be 0.7101 (0.5148-0.9795). The letter's "
                    "pooled JUPITER+HOPE-3 estimate is never an input."),
    "per_outcome": {MVE: "REPORTED_UNRESOLVED (>= 70 value in a report that is not held; relayed)",
                    MUS: "NOT_YET_RETRIEVED", DM: "NOT_YET_RETRIEVED"},
    "result_states": {MVE: {
        "state": "REPORTED_UNRESOLVED", "span": R_TITLE, "witness": W(R_REC, R_TITLE),
        "basis": "a held record names a report of HOPE-3 >= 70 analyses; the report itself is not held"}}}]
dump(kp, kd)

# ------------------------------------------------------------------ JUPITER >= 70 3-point MACE: a DIFFERENT outcome record
rp = "docs/relayed_values.json"
rvd = json.load(open(rp, encoding="utf-8"))
rvd["values"] = [v for v in rvd["values"] if not (v["topic"] == SLUG and v["trial"] == f"PMID {JUP}")]
rvd["values"].append({
    "topic": SLUG, "trial": f"PMID {JUP}", "outcome": MVE,
    "value": ("JUPITER >= 70 3-point MACE HR 0.61 (0.43-0.86) -- a DIFFERENT outcome record from the served broader JUPITER "
              "composite 0.61 (0.46-0.82); both are kept, neither replaces the other"),
    "relayed_by": "the orchestrating lane (statins-older-adults review fixtures, 2026-09-28)",
    "said_to_be_in": "Ridker 2017, Circulation (research letter, PMID 28385949)",
    "why_not_held": "the letter is not open: Europe PMC record only, no abstract; unpaywall no open location",
    "not_for": ["a substitute for the served composite", "the letter's pooled JUPITER+HOPE-3 estimate"]})
dump(rp, rvd)
print("statins fixtures written")
