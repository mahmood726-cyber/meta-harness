"""SGLT2-HFrEF review fixtures, 2026-09-28. Every span is asserted against held bytes first; no remembered counts.
 (1) Inventory: DEFINE-HF (PMID 31524498, NCT02653482; 263 randomised, LVEF <=40%, 12 weeks, NT-proBNP / KCCQ dual primary)
     and EMPERIAL-Reduced (NCT03448419; 312 randomised, 12 weeks, 6MWD primary; the SAME Abraham paper, PMID 33351892, as
     EMPERIAL-Preserved -- already declared in docs/multi_trial_reports.json as one article, two trials) are entered as
     known eligible trials. Neither reports a clinical event outcome: PUBLISHED_NO_TARGET_OUTCOME, and symptoms,
     biomarkers and walk distance are never relabelled as clinical events.
     EMPERIAL-Reduced safety: the paper's hypotension category (hypotension / orthostatic hypotension / syncope, 6/155 vs
     2/156) and ketoacidosis 0/155 vs 0/156 are RELAYED -- the paper is not held (no open copy). Held instead: the
     registry's CODED rows on safety denominators 155 / 156 (randomised 312) -- hypotension 2 vs 0, syncope 0 vs 1 --
     separate coded terms, never summed into the category, and a registry AE list with no ketoacidosis term bounds only
     what it lists, so 0 vs 0 is not claimed as REPORTED_ZERO_EVENTS from held bytes.
 (2) DAPA-HF harms: never absent by design. Table 2 (at least one dose, 2368 vs 2368): volume depletion 178 vs 162 and
     adjudicated DKA 3 vs 0 (all in patients with diabetes) are RELAYED, not held (NEJM 403; the Groningen PDF 403). The
     registry's coded rows (hypotension, orthostatic hypotension, syncope, dehydration; DKA / ketoacidosis / DKA coma) are
     a different definition and are never summed into the aggregate. If DKA 3 vs 0 is admitted, its zero cell takes the
     declared sparse-data method (harness/sparse_data.py).
 (3) EMPEROR-Reduced harms: the held report says 'Adverse events of interest are listed in Table S2' -- a supplement not
     held: REPORTED_UNRESOLVED, no counts.
  PYTHONPATH=. python outputs/handover/sglt2_sources/make_sglt2_hfref_fixtures.py"""
import hashlib, json, os, re

SLUG = "sglt2-hfref-hosp-cvdeath"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
PRIM = "Composite cardiovascular death or hospitalisation for heart failure"
VOL, DKA = "Volume depletion or hypotension", "Diabetic ketoacidosis"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"\{\n( +)\"", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


def rec(t, pmid):
    p = f"{H}/{t}/europepmc_record_{pmid}.json"
    r = json.load(open(p, encoding="utf-8"))["resultList"]["result"][0]
    assert r["pmid"] == pmid
    return p, r


# ------------------------------------------------------------------ (1) DEFINE-HF and EMPERIAL-Reduced
dp, dr = rec("DEFINE-HF", "31524498")
D_N = "In total, 263 patients were randomized to dapagliflozin 10 mg daily or placebo for 12 weeks."
D_PRIM = ("Dual primary outcomes were (1) mean NT-proBNP (N-terminal pro b-type natriuretic peptide) and (2) proportion of "
          "patients with ≥5-point increase in HF disease-specific health status on the Kansas City Cardiomyopathy "
          "Questionnaire overall summary score, or a ≥20% decrease in NT-proBNP.")
assert D_N in dr["abstractText"] and D_PRIM in dr["abstractText"]
ep, er = rec("EMPERIAL", "33351892")
E_N = "HF patients with reduced EF (HFrEF) (≤40%, N = 312, EMPERIAL-Reduced)"
E_PRIM = "The primary endpoint was 6-minute walk test distance (6MWTD) change to Week 12."
assert E_N in er["abstractText"] and E_PRIM in er["abstractText"]
ER = f"{H}/EMPERIAL-Reduced/NCT03448419.json"
erj = json.load(open(ER, encoding="utf-8"))
ae = erj["resultsSection"]["adverseEventsModule"]
grp = {g["id"]: g for g in ae["eventGroups"]}
emp = next(g for g in grp.values() if "Empagliflozin" in g["title"])
pla = next(g for g in grp.values() if "Placebo" in g["title"])
assert (emp["seriousNumAtRisk"], pla["seriousNumAtRisk"]) == (155, 156)
coded = {}
for e in ae.get("seriousEvents", []) + ae.get("otherEvents", []):
    if re.search(r"hypotens|syncope|ketoacid", e["term"], re.I):
        s = {x["groupId"]: x.get("numAffected") for x in e["stats"]}
        coded[e["term"]] = (s.get(emp["id"]), s.get(pla["id"]))
assert coded.get("Hypotension") == (2, 0) and coded.get("Syncope") == (0, 1), coded
assert not any("ketoacid" in t.lower() for t in coded)
DR = f"{H}/DEFINE-HF-registration/NCT02653482.json"
kp = "docs/known_eligible_missing.json"
kd = json.load(open(kp, encoding="utf-8"))
NTO = "PUBLISHED_NO_TARGET_OUTCOME"
kd["topics"][SLUG] = [e for e in kd["topics"].get(SLUG) or [] if e.get("trial") not in ("DEFINE-HF", "EMPERIAL-Reduced")] + [
    {"trial": "DEFINE-HF", "registration": "NCT02653482", "pmid": "31524498",
     "mechanism": "inventory (absent from the committed search); eligible by P/I/C/design (HFrEF, dapagliflozin vs placebo, randomised)",
     "status": "source_held_published",
     "acquisition": {"route": "acquisition cascade: Europe PMC record (abstract; not open access) + ClinicalTrials.gov registration",
                     "held_path": dp, "held_sha256": sha(dp), "registration_path": DR, "registration_sha256": sha(DR)},
     "design": "randomised, placebo-controlled; 263 randomised (registry actual enrolment 263); LVEF <=40%; 12 weeks",
     "design_note": ("its dual primary outcomes are a BIOMARKER (NT-proBNP) and a SYMPTOM/biomarker responder (KCCQ >= 5 "
                     "points or NT-proBNP -20%): never relabelled as clinical events"),
     "per_outcome": {PRIM: f"{NTO} (NT-proBNP / KCCQ; no CV death or HF hospitalisation outcome)",
                     VOL: "NOT_YET_RETRIEVED (the full report is not open)", DKA: "NOT_YET_RETRIEVED (the full report is not open)"},
     "result_states": {PRIM: {"state": NTO, "span": D_PRIM, "witness": W(dp, D_PRIM),
                              "basis": "the held abstract names its primary outcomes: a biomarker and a symptom/biomarker responder"}}},
    {"trial": "EMPERIAL-Reduced", "registration": "NCT03448419", "pmid": "33351892",
     "mechanism": "inventory (absent from the committed search); eligible by P/I/C/design (HFrEF, empagliflozin vs placebo)",
     "status": "source_held_record_and_registry",
     "acquisition": {"route": ("acquisition cascade: Europe PMC record of the joint EMPERIAL paper (one article, two trials; "
                               "docs/multi_trial_reports.json) + ClinicalTrials.gov posted results. The paper's full text is "
                               "not held (no open copy)"),
                     "held_path": ep, "held_sha256": sha(ep), "registration_path": ER, "registration_sha256": sha(ER)},
     "design": "randomised, double-blind, placebo-controlled; 312 randomised; safety set 155 empagliflozin vs 156 placebo; 12 weeks",
     "comparisons": "EMPERIAL-Reduced only (EMPERIAL-Preserved, the paper's other trial, is not an HFrEF population)",
     "design_note": ("its primary outcome is 6-minute walk distance; KCCQ and dyspnoea scores are symptoms: never relabelled as "
                     "clinical events. SAFETY (relayed, not held -- the paper is not open): hypotension category (hypotension / "
                     "orthostatic hypotension / syncope) 6/155 vs 2/156; ketoacidosis 0/155 vs 0/156. HELD (registry, coded "
                     f"terms on safety denominators 155/156): {'; '.join(f'{k} {v[0]} vs {v[1]}' for k, v in sorted(coded.items()))} "
                     "-- separate coded terms, never summed into the category; the registry names no ketoacidosis term, which "
                     "bounds only what it lists, so 0 vs 0 is not claimed from held bytes"),
     "per_outcome": {PRIM: f"{NTO} (6-minute walk distance; KCCQ / dyspnoea symptoms)",
                     VOL: "REPORTED_UNRESOLVED (category relayed 6/155 vs 2/156; registry coded rows held, never summed)",
                     DKA: "REPORTED_UNRESOLVED (0 vs 0 relayed; the paper is not held)"},
     "result_states": {PRIM: {"state": NTO, "span": E_PRIM, "witness": W(ep, E_PRIM),
                              "basis": "the joint paper's primary endpoint for both EMPERIAL trials is walk distance"}}}]
dump(kp, kd)

mp = "docs/multi_trial_reports.json"
md = json.load(open(mp, encoding="utf-8"))
rep = next(r for r in md["reports"] if r["report_id"] == "PMID 33351892")
tr = next(t for t in rep["trials"] if t["registration"] == "NCT03448419")
tr["registry_results"] = {
    "state": "SOURCE_HELD_EXAMINED_NOT_ADMITTED", "path": ER, "sha256": sha(ER),
    "findings": {"safety_denominators": "155 empagliflozin vs 156 placebo (adverse-event groups at risk); 312 randomised",
                 "coded_rows": {k: f"{v[0]} vs {v[1]}" for k, v in sorted(coded.items())},
                 "note": "coded terms are separate rows, never summed into the paper's hypotension category"}}
dump(mp, md)

# ------------------------------------------------------------------ (2) DAPA-HF: relayed aggregate, never summed codes
rp = "docs/relayed_values.json"
rvd = json.load(open(rp, encoding="utf-8"))
rvd["values"] = [v for v in rvd["values"] if not (v["topic"] == SLUG and v["trial"] == "PMID 31535829")]
for outcome, value in ((VOL, "volume depletion 178/2,368 dapagliflozin vs 162/2,368 placebo (Table 2, at least one dose)"),
                       (DKA, "adjudicated diabetic ketoacidosis 3/2,368 vs 0/2,368, all in patients with diabetes (Table 2); "
                             "a ZERO CELL: if admitted, the declared sparse-data method (0.5 added to all four cells of that "
                             "study only) applies")):
    rvd["values"].append({
        "topic": SLUG, "trial": "PMID 31535829", "outcome": outcome, "value": value,
        "relayed_by": "the orchestrating lane (SGLT2-HFrEF review fixtures, 2026-09-28)",
        "said_to_be_in": "DAPA-HF, NEJM 2019, Table 2",
        "why_not_held": ("NEJM PDF 403; the Groningen repository PDF 403; Europe PMC not open access (recorded). The registry's "
                         "posted rows are CODED terms (hypotension, orthostatic hypotension, syncope, dehydration; diabetic "
                         "ketoacidosis, ketoacidosis, DKA coma): a different definition, never summed into the aggregate"),
        "not_for": ["a sum of the registry's coded rows"]})
dump(rp, rvd)

# ------------------------------------------------------------------ (3) EMPEROR-Reduced: reported in an unheld supplement
E_TXT = f"{H}/EMPEROR-Reduced/unpaywall.local.txt"
E_PDF = f"{H}/EMPEROR-Reduced/unpaywall.pdf"
ET = flat(open(E_TXT, encoding="utf-8").read())
S2 = "Adverse events of interest are listed in Table S2."
EXCL = "The 4 patients in the placebo group who did not receive placebo were excluded from the safety analyses."
for s in (S2,):
    assert ET.count(s) == 1, s
assert flat(EXCL) in ET or "who did not receive placebo were excluded from the safety analyses" in ET
EXC = f"{X}/EMPEROR-Reduced_adverse_events_sentence.txt"
open(EXC, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (verbatim sentences) of EMPEROR-Reduced (Packer et al., NEJM 2020), Glasgow repository copy (CC BY-SA, "
    f"accepted version), held locally\n# held PDF: {E_PDF} sha256 {sha(E_PDF)}\n\n{S2}\n")
ve_p = f"cache/{SLUG}/verified_effects.json"
ve = json.load(open(ve_p, encoding="utf-8"))
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])
for outcome in (VOL, DKA):
    rows = [r for r in as_list(ve.get("32865377")) if r.get("outcome") != outcome]
    rows.append({"outcome": outcome, "absent": True, "override": True, "provenance": "REFUSED_ON_EVIDENCE",
                 "document_ref": EXC, "source_span": S2, "reported_unresolved_span": S2,
                 "reason": ("EMPEROR-Reduced reports its adverse events of interest in Table S2 of its supplement, which is not "
                            "held: the outcome is reported, the counts are not extracted, and none is supplied from memory")})
    ve["32865377"] = rows if len(rows) > 1 else rows[0]
dump(ve_p, ve)
print("SGLT2-HFrEF fixtures written")
