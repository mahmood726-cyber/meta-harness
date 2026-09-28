"""MRA-HFrEF mortality (spironolactone-hfref-mortality) fixtures, 2026-09-28. Every span is asserted against held bytes first.
 (1) PHASES: EMPHASIS-HF's registry carries ONE design field -- NON_RANDOMIZED / SINGLE_GROUP / NONE, one 'Eplerenone arm'
     -- while its own posted results name a 'Double-blind (DB) Phase' (eplerenone and placebo groups) and an 'Open Label
     Phase' (eplerenone only; 1,246 of the 1,597 who completed the double-blind phase entered it). The design field is
     the EXTENSION's. Modelled trial -> phase -> comparison -> analysis period (docs/trial_phases.json): the family is
     screened on the randomised phase; the extension keeps its own design and never supplies, redefines or inherits the
     comparison (harness/trial_family.attach_phases, fail closed). The served mortality HR 0.76 is the double-blind
     phase to the 25 May 2010 cut-off (the registry: 'analysis was only performed ... up to cut-off').
 (2) SAFETY, population-specific denominators, definitions kept distinct (outcome_restrictions DEFINITION_TYPED):
     J-EMPHASIS-HF Table 5 (held, J-STAGE; >= 1 dose): investigator-reported hyperkalaemia 8/111 vs 6/110 -- admitted;
     gynaecomastia 0 vs 0 is gynaecomastia ALONE -- never a zero for 'gynaecomastia or breast pain'.
     RALES (NEJM 1999, not held): serious hyperkalaemia 14/822 vs 10/841; gynaecomastia or breast pain among MEN
     61/603 vs 9/614 (the table's unique-patient aggregate; its overlapping rows are never summed) -- RELAYED.
     EMPHASIS-HF laboratory-threshold counts (K > 5.5): not held (NEJM 403; the registry posts only adjudicated
     HOSPITALISATION for hyperkalaemia, 4 vs 3 -- another definition); never computed from the abstract's percentages.
 (3) J-EMPHASIS-HF all-cause mortality: its own Table 3 HR 1.77 (0.81-3.87), 17/111 vs 10/110 -- replacing the composite
     primary HR 0.85 that source_hierarchy surfaced through the ROLE anchor 'primary endpoint' (fixed in the harness).
 (4) Udelson 2010 (PMID 20299607) is seeded into the search and screened like any record.
  PYTHONPATH=. python outputs/handover/mra_sources/make_mra_fixtures.py"""
import hashlib, json, os, re

SLUG = "spironolactone-hfref-mortality"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
REC = f"cache/{SLUG}/records.json"
BY = "evidence lane (Claude Opus 5.5), 2026-09-28, source-backed"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
ACM, HK, GYN = "All-cause mortality", "Hyperkalemia", "Gynecomastia or breast pain"
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"\{\n( +)\"", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


def held(path, span, where, once=False):
    n = flat(open(path, encoding="utf-8").read()).count(flat(span))
    assert n >= 1 and (n == 1 or not once), f"{where}: {n} occurrences of {span!r} in {path}"
    return span


# ------------------------------------------------------------------ (1) EMPHASIS-HF: trial -> phase -> comparison -> period
R_EM = f"{H}/EMPHASIS-HF-registration/NCT00232180.json"
reg = json.load(open(R_EM, encoding="utf-8"))
dm = reg["protocolSection"]["designModule"]["designInfo"]
assert (dm["allocation"], dm["interventionModel"], dm["maskingInfo"]["masking"]) == ("NON_RANDOMIZED", "SINGLE_GROUP", "NONE")
P_DB = held(R_EM, "Double-blind (DB) Phase", "DB period")
P_OL = held(R_EM, "A total of 1597 participants who completed the double-blind phase, 1246 entered into the open-label "
                  "phase and 351 participants were ineligible to participate the open-label phase.", "flow", once=True)
G_E = held(R_EM, "Eplerenone: Double-blind Phase", "eplerenone DB group")
G_P = held(R_EM, "Placebo: Double-blind Phase", "placebo DB group")
G_PD = held(R_EM, "Placebo matching to eplerenone 25 mg orally once daily on top of standard heart failure therapy.", "placebo")
G_OL = held(R_EM, "Eplerenone: Open Label Phase", "OLE group")
G_OLD = held(R_EM, "Participants from double blind phase received eplerenone 25 mg tablet orally once daily on top of "
                   "standard heart failure therapy for 12 months.", "OLE description")
CUT = held(R_EM, "The statistical analysis was only performed on the adjudicated endpoint data up to cut-off.", "cut-off")
EM_R = held(REC, "In this randomized, double-blind trial, we randomly assigned 2737 patients with New York Heart Association "
                 "class II heart failure and an ejection fraction of no more than 35% to receive eplerenone (up to 50 mg "
                 "daily) or placebo, in addition to recommended therapy.", "EMPHASIS-HF randomisation")
EM_HR = held(REC, "A total of 12.5% of patients receiving eplerenone and 15.5% of those receiving placebo died (hazard ratio, "
                  "0.76; 95% CI, 0.62 to 0.93; P=0.008)", "EMPHASIS-HF mortality HR")
tp = "docs/trial_phases.json"
tph = json.load(open(tp, encoding="utf-8")) if os.path.exists(tp) else {
    "_doc": ("TRIAL -> PHASE -> COMPARISON -> ANALYSIS PERIOD (harness/trial_family.phase_declaration / attach_phases). A "
             "registry carries ONE design field; for a trial with a randomised phase and a later extension it can describe "
             "the extension. The family is screened on its RANDOMISED phase; an EXTENSION keeps its own design and never "
             "supplies, redefines or inherits the comparison (fail closed). Witnesses re-verified against held bytes."),
    "topics": {}}
tph["topics"].setdefault(SLUG, {})["NCT00232180"] = {
    "registry_design_field_describes": "OPEN_LABEL_EXTENSION",
    "basis": ("the registry's single design field (NON_RANDOMIZED / SINGLE_GROUP / NONE) and its one 'Eplerenone arm' match "
              "the open-label phase; its own posted results name a double-blind phase with eplerenone and placebo groups, "
              "and the primary report states the randomised, double-blind comparison"),
    "decided_by": BY,
    "phases": [
        {"phase_id": "DOUBLE_BLIND", "kind": "RANDOMISED", "label": "Double-blind (DB) Phase",
         "design": {"allocation": "RANDOMIZED", "intervention_model": "PARALLEL", "masking": "DOUBLE"},
         "comparisons": [{
             "comparison_id": "eplerenone-vs-placebo",
             "arms": [{"label": G_E, "interventions": ["Eplerenone"]}, {"label": G_P, "interventions": ["Placebo"]}],
             "analysis_periods": [
                 {"period_id": "DB_TO_CUTOFF_2010-05-25", "served": True,
                  "basis": "the published analysis (HR 0.76) and the registry's only analysed period"},
                 {"period_id": "COMPLETE_DB_TO_2011-03-18", "served": False,
                  "basis": "registry counts only (205 vs 253 deaths), no posted hazard ratio; not the published analysis"}]}],
         "witnesses": [{"kind": "registry results: period", "witness": W(R_EM, P_DB)},
                       {"kind": "registry results: eplerenone group", "witness": W(R_EM, G_E)},
                       {"kind": "registry results: placebo group", "witness": W(R_EM, G_P)},
                       {"kind": "registry results: placebo description", "witness": W(R_EM, G_PD)},
                       {"kind": "registry results: analysed period", "witness": W(R_EM, CUT)},
                       {"kind": "report: randomised double-blind comparison", "witness": W(REC, EM_R)},
                       {"kind": "report: mortality HR", "witness": W(REC, EM_HR)}]},
        {"phase_id": "OPEN_LABEL_EXTENSION", "kind": "EXTENSION", "label": "Open Label Phase",
         "design": {"allocation": "NON_RANDOMIZED", "intervention_model": "SINGLE_GROUP", "masking": "NONE"},
         "arms": [{"label": G_OL, "interventions": ["Eplerenone"]}], "comparisons": [],
         "witnesses": [{"kind": "registry results: participant flow", "witness": W(R_EM, P_OL)},
                       {"kind": "registry results: open-label group", "witness": W(R_EM, G_OL)},
                       {"kind": "registry results: open-label description", "witness": W(R_EM, G_OLD)}]}]}
dump(tp, tph)

# ------------------------------------------------------------------ J-EMPHASIS-HF: Tables 3 and 5 (held J-STAGE PDF)
J_PDF, J_TXT = f"{H}/J-EMPHASIS-HF/unpaywall.pdf", f"{H}/J-EMPHASIS-HF/unpaywall.local.txt"
JT = flat(open(J_TXT, encoding="utf-8").read())
T3 = "Table 3. Primary and Secondary Outcomes in the J-EMPHASIS-HF Study"
T3_D = "Death from any cause 17 (15.3) 10 (9.1) 1.77 (0.81, 3.87) 0.15"
T5 = ("Table 5. Selected Investigator-Reported Adverse Events, and Those Leading to Permanent Withdrawal of the Study Drug, "
      "According to Study Group in the J-EMPHASIS-HF Study*")
T5_HK = "Hyperkalemia 8 (7.2) 6 (5.5) 0.78 2 (1.8) 1 (0.9) 1.00"
T5_GY = "Gynecomastia 0 0 – 0 0 –"
T5_F = "*Patients who received at least one dose of the study drug were included in this safety analysis."
for s in (T3, T3_D, T5, T5_HK, T5_GY, T5_F):
    assert JT.count(flat(s)) == 1, s
EXC = f"{X}/J-EMPHASIS-HF_Tables3_5.tables.txt"
rows_t3 = ["TABLE " + T3, "Outcome | Eplerenone (n=111) | Placebo (n=110) | Hazard ratio (95% CI) | P value",
           "Death from any cause | 17 (15.3) | 10 (9.1) | 1.77 (0.81, 3.87) | 0.15"]
rows_t5 = ["TABLE " + T5, "Event | Eplerenone (n=111) adverse event | Placebo (n=110) adverse event | P value | "
           "Eplerenone leading to discontinuation | Placebo leading to discontinuation | P value",
           "Hyperkalemia | 8 (7.2) | 6 (5.5) | 0.78 | 2 (1.8) | 1 (0.9) | 1.00",
           "Gynecomastia | 0 | 0 | – | 0 | 0 | –", T5_F]
open(EXC, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of J-EMPHASIS-HF (Tsutsui et al., Circ J 2018) Tables 3 and 5, J-STAGE PDF (free to read, no licence stated);"
    " held locally, not redistributed. Every value is verbatim from our text of the held document; the CELL BOUNDARIES "
    "are this excerpt's segmentation. Table 5 counts are PATIENTS who received at least one dose.\n"
    f"# held: {J_PDF} sha256 {sha(J_PDF)}\n\n"
    "=== TABLES (excerpt) ===\n" + "\n".join(rows_t3 + rows_t5) + "\n")
D_ROW = "Death from any cause | 17 (15.3) | 10 (9.1) | 1.77 (0.81, 3.87) | 0.15"
HK_ROW = "Hyperkalemia | 8 (7.2) | 6 (5.5) | 0.78 | 2 (1.8) | 1 (0.9) | 1.00"
GY_ROW = "Gynecomastia | 0 | 0 | – | 0 | 0 | –"

# ------------------------------------------------------------------ hand entries
va_p, ve_p = f"cache/{SLUG}/verified_arms.json", f"cache/{SLUG}/verified_effects.json"
va, ve = json.load(open(va_p, encoding="utf-8")), json.load(open(ve_p, encoding="utf-8"))
J = "28824029"
ja = [r for r in as_list(va.get(J)) if r.get("outcome") != HK]
ja.append({"outcome": HK, "ai": 8, "n1i": 111, "ci": 6, "n2i": 110, "kind": "extracted_counts",
           "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
           "document_ref": EXC, "document_sha256": sha(EXC), "source_span": HK_ROW,
           "safety_population": "patients who received at least one dose, 111 vs 110",
           "safety_window": "the trial's safety analysis (as tabulated)",
           "harm_definition": "investigator-reported adverse event of hyperkalaemia (Table 5)",
           "harm_definition_key": "HYPERKALAEMIA_INVESTIGATOR_REPORTED",
           "supersedes": {"provenance": "REFUSED_ON_EVIDENCE",
                          "declared_in": "scripts/hm3_screening_supersession.py HARM_DECISIONS_SUPERSEDED"},
           "reason": ("Hyperkalaemia from the trial's own Table 5: investigator-reported adverse events, 8/111 vs 6/110 "
                      "(patients with at least one dose). Not serious hyperkalaemia and not a laboratory threshold.")})
va[J] = ja
je = [r for r in as_list(ve.get(J)) if r.get("outcome") not in (ACM, HK, GYN)]
je += [
    {"outcome": ACM, "override": True, "effect": 1.77, "ci_low": 0.81, "ci_high": 3.87, "scale": "HR",
     "provenance": "fulltext_verified", "source_level": 1, "document_ref": EXC, "document_sha256": sha(EXC),
     "source_span": D_ROW,
     "source": (f"{EXC}: J-EMPHASIS-HF Table 3, death from any cause 17 (15.3) vs 10 (9.1), hazard ratio 1.77 "
                "(0.81, 3.87) -- the trial's own all-cause mortality HR; replaces the composite primary HR 0.85")},
    {"outcome": GYN, "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE", "override": True, "source_level": 1,
     "document_ref": EXC, "document_sha256": sha(EXC), "source_span": GY_ROW,
     "held_out_row": {"ai": 0, "n1i": 111, "ci": 0, "n2i": 110},
     "not_admitted_because": "gynaecomastia alone; breast pain is not reported -- a narrower outcome than the composite",
     "reason": ("Table 5 reports GYNAECOMASTIA alone, 0 vs 0; breast pain is not reported. 'No gynaecomastia' is not a "
                "zero for 'gynaecomastia or breast pain': the row is held out, never counted as a zero-event trial.")}]
ve[J] = je

RALES, EMPH = "10471456", "21073363"
R_SER = held(REC, "The incidence of serious hyperkalemia was minimal in both groups of patients.", "RALES serious K")
R_GYN = held(REC, "Gynecomastia or breast pain was reported in 10 percent of men who were treated with spironolactone, as "
                  "compared with 1 percent of men in the placebo group (P<0.001).", "RALES gynaecomastia")
NOT_HELD_R = ("RALES (NEJM 1999) is not held: the NEJM PDF returned 403 and Europe PMC holds no open-access copy "
              "(evidence/acquisition_cascade/ATTEMPTS.jsonl)")
# RALES's and EMPHASIS-HF's refusals are PINNED HM3 decisions (docs/evidence/hm3-held-source-audit/decisions.json): they
# stay verbatim. What this round adds reaches their rows without rewriting them: the RELAYED values
# (docs/relayed_values.json) and the typed DEFINITIONS (docs/outcome_restrictions.json, below).
for pid, outcome, span in ((RALES, HK, R_SER), (RALES, GYN, R_GYN)):
    assert any(r.get("outcome") == outcome and r.get("provenance") == "REFUSED_ON_EVIDENCE" and r.get("source_span") == span
               for r in as_list(ve.get(pid))), (pid, outcome, "the pinned refusal must stay verbatim")

E_LAB = held(REC, "A serum potassium level exceeding 5.5 mmol per liter occurred in 11.8% of patients in the eplerenone group "
                  "and 7.2% of those in the placebo group (P<0.001).", "EMPHASIS-HF lab threshold")
assert any(r.get("outcome") == HK and r.get("provenance") == "REFUSED_ON_EVIDENCE" for r in as_list(ve.get(EMPH))),     "EMPHASIS-HF's pinned refusal must stay verbatim (its counts are not held and never computed from percentages)"
dump(va_p, va)
dump(ve_p, ve)

rp = "docs/relayed_values.json"
rvd = json.load(open(rp, encoding="utf-8"))
rvd["values"] = [v for v in rvd["values"] if not (v["topic"] == SLUG and v["trial"] == f"PMID {RALES}")]
for outcome, value, where in (
        (HK, "serious hyperkalaemia 14/822 spironolactone vs 10/841 placebo", "RALES, NEJM 1999 (serious hyperkalaemia)"),
        (GYN, "gynaecomastia or breast pain among MEN 61/603 vs 9/614 (men-only denominators; unique-patient aggregate)",
         "RALES, NEJM 1999 (adverse-event table)")):
    rvd["values"].append({"topic": SLUG, "trial": f"PMID {RALES}", "outcome": outcome, "value": value,
                          "relayed_by": "the orchestrating lane (MRA-HFrEF mortality review fixtures, 2026-09-28)",
                          "said_to_be_in": where, "why_not_held": NOT_HELD_R,
                          "not_for": ["a sum of the table's overlapping rows", "an all-patient denominator (men only)"]
                          if outcome == GYN else ["a laboratory-threshold or investigator-reported count"]})
dump(rp, rvd)

# ------------------------------------------------------------------ hyperkalaemia definitions typed per trial
J_EXC_HK = "Hyperkalemia | 8 (7.2) | 6 (5.5) | 0.78 | 2 (1.8) | 1 (0.9) | 1.00"
op = "docs/outcome_restrictions.json"
orx = json.load(open(op, encoding="utf-8"))
orx["topics"].setdefault(SLUG, {})[HK] = {
    "restriction": "DEFINITION_TYPED",
    "definition": ("serious / investigator-reported / laboratory-threshold hyperkalaemia are DIFFERENT definitions; a pool "
                   "never spans them"),
    "definitions_by_trial": {
        J: {"key": "HYPERKALAEMIA_INVESTIGATOR_REPORTED", "definition": "investigator-reported adverse event (Table 5)",
            "witness": W(EXC, J_EXC_HK)},
        RALES: {"key": "HYPERKALAEMIA_SERIOUS", "definition": "serious hyperkalaemia", "witness": W(REC, R_SER)},
        EMPH: {"key": "HYPERKALAEMIA_LAB_GT_5_5", "definition": "serum potassium > 5.5 mmol/L", "witness": W(REC, E_LAB)}}}
dump(op, orx)

# ------------------------------------------------------------------ (4) Udelson 2010: SCREENED by the harness, inventoried
# The committed search is a frozen snapshot (fetch.ensure never re-runs it), so a query added to the topic would claim a
# search that never ran. Instead the harness's own screener is RUN on the held record under this topic's protocol, and its
# decision is recorded with the inventory entry (tests re-run it against the held bytes).
import html as _h, sys
sys.path.insert(0, ".")
from harness import screen as _screen
cfg = json.load(open(f"topics/{SLUG}.json", encoding="utf-8"))
U_REC = f"{H}/Udelson-2010/europepmc_record_20299607.json"
_u = json.load(open(U_REC, encoding="utf-8"))
_u = (_u.get("resultList") or {}).get("result", [_u])[0] if "resultList" in _u else _u
U_ABS = flat(_h.unescape(re.sub(r"<[^>]+>", " ", _u.get("abstractText", ""))))
urec = {"id": "20299607", "id_type": "pmid", "title": _u["title"], "abstract": U_ABS,
        "pubtypes": list((_u.get("pubTypeList") or {}).get("pubType") or []), "year": _u.get("pubYear"), "doi": _u.get("doi")}
dec = _screen.screen_record(urec, cfg["include"], set(cfg.get("negative_control_pmids") or []))
assert dec.decision == "include", dec
U_DESIGN = held(U_REC, "Of the total 226 patients enrolled, 117 were randomly assigned to receive eplerenone and 109 to "
                       "receive placebo.", "Udelson randomisation")
U_PRIM = held(U_REC, "The primary efficacy analysis was the between-group comparison of the change in LV end-diastolic volume "
                     "index.", "Udelson primary")
kp = "docs/known_eligible_missing.json"
kd = json.load(open(kp, encoding="utf-8"))
kd["topics"][SLUG] = [e for e in kd["topics"].get(SLUG) or [] if e.get("pmid") != "20299607"] + [{
    "trial": "Udelson 2010 (eplerenone LV remodelling)", "registration": None, "pmid": "20299607",
    "mechanism": ("inventory (absent from the committed search snapshot); SCREENED by harness.screen.screen_record on the held "
                  "record under this topic's protocol"),
    "screening": {"decision": dec.decision, "rule_id": dec.rule_id, "reason": dec.reason, "evidence": dec.evidence,
                  "screened_by": "harness.screen.screen_record (topic include rules; re-run by tests on the held record)"},
    "status": "source_held_published",
    "acquisition": {"route": "acquisition cascade: Europe PMC record (abstract; not open access); no registration found in "
                             "the record", "held_path": U_REC, "held_sha256": sha(U_REC)},
    "design": "randomised, double-blind, placebo-controlled; 226 randomised (117 eplerenone, 109 placebo); NYHA II/III, "
              "LVEF <= 35%; 36 weeks",
    "design_note": ("its primary is LV REMODELLING (end-diastolic volume index): eligibility is on P/I/C/design, so the "
                    "remodelling primary does not exclude it, and it supplies no mortality hazard ratio"),
    "per_outcome": {
        ACM: "NOT_YET_RETRIEVED (the held abstract reports no deaths; the full report is not open -- no mortality HR is "
             "supplied and none is inferred)",
        HK: "NOT_YET_RETRIEVED (the full report is not open)",
        GYN: "NOT_YET_RETRIEVED (the full report is not open)"},
    "result_states": {ACM: {
        "state": "NOT_YET_RETRIEVED", "span": U_PRIM, "witness": W(U_REC, U_PRIM),
        "basis": ("the held abstract names a remodelling primary and reports no deaths; the full report is not open, so "
                  "whether it reports deaths is unknown -- never 'not reported', never a zero")}},
    "witnesses": [{"kind": "randomisation", "witness": W(U_REC, U_DESIGN)}]}]
dump(kp, kd)
print("MRA-HFrEF fixtures written")
