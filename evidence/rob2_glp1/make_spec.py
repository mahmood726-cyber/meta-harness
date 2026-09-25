"""Write SPEC.json: the lane's RoB 2 proposals for the 3-point MACE result of each GLP-1 trial. Witnesses are spans the
lane read and chose (each given here by its held ref plus the first words of the span as it appears in the render);
anchors are derived and then CHECKED to reproduce exactly the chosen span, so the builder cannot silently pin a
different passage. Judgements follow the RoB 2 signalling logic and are PROPOSALS for human review.
  python evidence/rob2_glp1/make_spec.py && python evidence/rob2_glp1/build_rob2.py"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evidence", "scripts"))
os.chdir(ROOT)
import textrep  # noqa: E402

H = "evidence/held_local"
REG = "evidence/held/registry"
STATR_ELIXA = "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf"


def span_from(ref, start, end):
    """The render text from `start` through the first `end` after it (the chosen span)."""
    t = textrep.render(ref)
    i = t.find(start)
    if i < 0:
        sys.exit(f"REFUSED: start not in {ref}: {start[:70]!r}")
    j = t.find(end, i)
    if j < 0:
        sys.exit(f"REFUSED: end not in {ref}: {end[:70]!r}")
    return {"ref": ref, "start": start, "end": end, "kind": kind_of(ref), "_span": t[i:j + len(end)]}


def kind_of(ref):
    if "/registry/" in ref:
        return "registry"
    if "SAP" in ref:
        return "sap"
    if "Prot_" in ref:
        return "protocol"
    if "FDA_" in ref or "glp1_regulatory" in ref:
        return "regulator"
    return "paper"


W = span_from
T = {
 "PIONEER 6": {"pmid": "31185157", "nct": "NCT02692716", "domains": {
   "D1_randomisation": ("low", "Sequence by IV/WRS (central, concealed), stratified; baseline similar.",
       [W(f"{H}/PMC6587508/fullText.xml", "Randomization was performed using an interactive voice/web response system", "visually identical oral sem"),
        W(f"{H}/31185157/radboud_208030.pdf", "Baseline characteristics were similar in the two groups.", "in the two groups.")]),
   "D2_deviations_assignment": ("low", "Double-blind with matching placebo; all analyses in the full analysis set = all randomised (ITT, as randomised).",
       [W(f"{H}/31185157/radboud_208030.pdf", "All analyses involved the full analysis set, which included all randomly assigned patients.", "all randomly assigned patients."),
        W(f"{H}/NCT02692716/SAP_001.pdf", "The statistical evaluation of the FAS will follow the intention-to-treat (ITT) principle", "“as randomised”.")]),
   "D3_missing_outcome_data": ("low", "Vital status collected for the 11 non-completers: every randomised patient accounted for.",
       [W(f"{H}/31185157/radboud_208030.pdf", "Vital-status information was collected for the 11 patients who did not complete the trial", "all patients who took part.")]),
   "D4_outcome_measurement": ("low", "Events adjudicated by an independent external committee unaware of trial-group assignments.",
       [W(f"{H}/31185157/radboud_208030.pdf", "Cardiovascular and other selected events were adjudicated by an independent", "unaware of the trial-group assignments.")]),
   "D5_selection_of_reported_result": ("low", "Protocol (not registry) fixes 3-point MACE as the primary endpoint; the SAP keeps treatment blinding until database release (analysis plan fixed before unblinding).",
       [W(f"{H}/NCT02692716/Prot_000.pdf", "The primary endpoint is time from randomisation to first occurrence of a MACE composite endpoint", "or non-fatal stroke."),
        W(f"{H}/NCT02692716/SAP_001.pdf", "The blinding of the randomised treatments will be maintained until the database has been released", "for statistical analysis.")])},
   "D2_treatment_discontinuation": ("more permanently discontinued oral semaglutide (11.6% vs 6.5%); follow-up continued",
       [W(f"{H}/31185157/radboud_208030.pdf", "More patients permanently discontinued oral semaglutide than placebo", "Supplementary Appendix).")])},
 "SUSTAIN-6": {"pmid": "27633186", "nct": "NCT01720446", "domains": {
   "D1_randomisation": ("some_concerns", "Stratified (9 strata) and balanced at baseline, but no held source describes sequence generation or allocation concealment (RoB 2 1.1/1.2 = NI); the FDA medical review also records stratification errors.",
       [W(f"{H}/FDA_209637/StatR.pdf", "All of these baseline demographic characteristics appeared balanced between the two treatment arms.", "two treatment arms."),
        W(f"{H}/FDA_209637/MedR.pdf", "The majority of the site-level PDs and approximately three-quarter of the patient-level PDs", "incorrect stratification")]),
   "D2_deviations_assignment": ("low", "Double-blind within dose group; FAS analysed by ITT as randomised.",
       [W(f"{H}/FDA_209637/StatR.pdf", "The SUSTAIN 6 trial was a multi-national, randomized, double-blind", "cardiovascular safety of semaglutide."),
        W(f"{H}/FDA_209637/StatR.pdf", "The statistical evaluation of the FAS follow ed the intention-to-treat (ITT) principle", "“as randomized”.")]),
   "D3_missing_outcome_data": ("low", "Vital status for 99.6% of all randomised; 13 lacked it (6 vs 7).",
       [W(f"{H}/FDA_209637/StatR.pdf", "vital status was available for 99.6% of all randomized subjects", "7 with placebo).")]),
   "D4_outcome_measurement": ("low", "External independent EAC adjudicating in a blinded manner.",
       [W(f"{H}/FDA_209637/StatR.pdf", "An external independent Event Adjudication Committee (EAC) was constituted", "independent and blinded manner.")]),
   "D5_selection_of_reported_result": ("low", "The FDA statistical reviewer, reading the protocol/SAP, states the MACE time-to-first-event analysis was pre-specified; no dated SAP is held -- a human should weigh a regulator's statement vs a dated plan.",
       [W(f"{H}/FDA_209637/StatR.pdf", "The primary analysis of MACE was pre-specified as a time to first event analysis.", "time to first event analysis."),
        W(f"{H}/FDA_209637/StatR.pdf", "Endpoints and methods of analysis are specified in the protocols/statistical analysis plans.", "statistical analysis plans.")])},
   "D2_treatment_discontinuation": ("more discontinued semaglutide for adverse events (abstract)",
       [W("evidence/held/27633186/europepmc_core.json", "Fewer serious adverse events occurred in the semaglutide group", "mainly gastrointestinal.")])},
 "LEADER": {"pmid": "27295427", "nct": "NCT01179048", "domains": {
   "D1_randomisation": ("some_concerns", "1:1, stratified by eGFR; no held source describes sequence generation or allocation concealment (1.1/1.2 = NI) and no baseline-balance statement is bound.",
       [W(f"{H}/PMC4985288/efetch.xml", "Randomization was stratified according to the estimated glomerular filtration rate", "at screening")]),
   "D2_deviations_assignment": ("low", "Double-blind, matching placebo; all randomised included in the primary analysis.",
       [W(f"{H}/PMC4985288/efetch.xml", "We performed this multicenter, double-blind, placebo-controlled trial", "32 countries."),
        W(f"{H}/PMC4985288/efetch.xml", "All the patients who underwent randomization were included in the primary and exploratory analyses", "primary and exploratory analyses")]),
   "D3_missing_outcome_data": ("low", "Vital status known for 99.7%; 96.8% completed a final visit, died or had a primary outcome.",
       [W(f"{H}/PMC4985288/efetch.xml", "The vital status was known in 99.7% of the patients.", "99.7% of the patients."),
        W(f"{H}/PMC4985288/efetch.xml", "A total of 96.8% of the patients completed a final visit", "had a primary outcome.")]),
   "D4_outcome_measurement": ("low", "Adjudicated in a blinded fashion by an external independent committee.",
       [W(f"{H}/PMC4985288/efetch.xml", "all of which were adjudicated in a blinded fashion", "event-adjudication committee.")]),
   "D5_selection_of_reported_result": ("low", "The 2013 design paper (published before the 2016 results) fixes 3-point MACE as the primary end point; protocol and SAP published with the article (not held here).",
       [W("evidence/held/24176437/europepmc_core.json", "The primary end point is the time from randomization to a composite outcome", "or nonfatal stroke."),
        W(f"{H}/PMC4985288/efetch.xml", "The statistical analysis plan is available with the protocol at NEJM.org.", "at NEJM.org.")])},
   "D2_treatment_discontinuation": ("time on regimen 84% vs 83%; more stopped liraglutide for adverse events",
       [W(f"{H}/PMC4985288/efetch.xml", "The mean percentage of time that patients received the trial regimen was 84%", "83% for placebo.")])},
 "SOUL": {"pmid": "40162642", "nct": "NCT03914326", "domains": {
   "D1_randomisation": ("low", "Central IWRS randomisation 1:1 (sequence and concealment via the system); baseline balance not held (1.3 = NI, which RoB 2 allows at low).",
       [W(f"{H}/UCL_10169247/soul_design.pdf", "Randomization was performed using an interactive web response system", "3 weeks afterwards.")]),
   "D2_deviations_assignment": ("some_concerns", "Blinded (visually identical tablets), but the analysis population for MACE is not bound: the protocol's FAS text sits in a letter-spaced PDF text layer that does not render (2.6 = NI).",
       [W(f"{H}/UCL_10169247/soul_design.pdf", "Blinding of investigational product was maintained through using visually identical oral semaglutide", "in identical packaging.")]),
   "D3_missing_outcome_data": ("NO_EVIDENCE_HELD", "The NEJM results paper is not held (no PMC copy; the repository returned 403) and the registry participant flow is not in the lane's render: no vital-status or completeness figure is held. NOT relabelled high.", []),
   "D4_outcome_measurement": ("low", "Central adjudication by a masked external committee.",
       [W(f"{H}/UCL_10169247/soul_design.pdf", "Potential CV and kidney outcome events, along with selected AEs, underwent central adjudication by a masked external", "tion committee,")]),
   "D5_selection_of_reported_result": ("low", "The 2023 design paper (before the 2025 results) fixes 3-point MACE as the primary outcome.",
       [W(f"{H}/UCL_10169247/soul_design.pdf", "The primary trial outcome is time from randomization (week 0) to first occurrence of adjudication-confirmed MACE", "or nonfatal stroke).")])}},
 "AMPLITUDE-O": {"pmid": "34215025", "nct": "NCT03496298", "domains": {
   "D1_randomisation": ("low", "Central IRT with a permuted-block schedule (sequence + concealment).",
       [W(f"{H}/NCT03496298/SAP_001.pdf", "Patients who meet all eligibility criteria will be randomized centrally by an Interactive Response Technology", "permuted-block randomization schedule")]),
   "D2_deviations_assignment": ("low", "Identically appearing blinded syringes; efficacy analysis in the ITT population.",
       [W(f"{H}/34215025/enlighten_246785.pdf", "The trial medications and placebo were provided in iden- tically appearing prefilled syringes", "in a blinded manner."),
        W(f"{H}/NCT03496298/SAP_001.pdf", "The efficacy analysis population will be the ITT population.", "the ITT population.")]),
   "D3_missing_outcome_data": ("low", "Vital status known for 99.9%; primary-outcome status known for 96.7% (the 3.3% gap is noted for the reviewer).",
       [W(f"{H}/34215025/enlighten_246785.pdf", "status with respect to the primary outcome was known for 3941 of the 4076 participants", "Supplementary Appendix).")]),
   "D4_outcome_measurement": ("low", "Independent end-point committee unaware of trial-group assignments.",
       [W(f"{H}/34215025/enlighten_246785.pdf", "An independent clinical end-point committee, the members of which were unaware of the trial", "and pancreatic events.")]),
   "D5_selection_of_reported_result": ("low", "Protocol amendment approved 30 July 2018 (before the 2021 results) defines the adjudicated MACE outcome. The paper's sentence that analyses followed prespecified plans finalised before unblinding is NOT bound here (a line break in the held PDF defeats the anchor), so D5 rests on the protocol alone -- weigh accordingly.",
       [W(f"{H}/NCT03496298/Prot_000.pdf", "Approval Date: 30 July 2018", "30 July 2018"),
        W(f"{H}/NCT03496298/Prot_000.pdf", "Time to the first occurrence of any of the following clinical events, positively adjudicated by the Clinical Endpoint Committee", "(CEC):")])},
   "D2_treatment_discontinuation": ("exposure 88.9% vs 91.1% of follow-up time; followed to trial end regardless of adherence",
       [W(f"{H}/34215025/enlighten_246785.pdf", "Unless consent was revoked, participants were followed until the end of the trial", "regardless of adherence.")])},
 "REWIND": {"pmid": "31189511", "nct": "NCT01394952", "domains": {
   "D1_randomisation": ("low", "Computer-generated random sequence via IVRS (concealed), 1:1, stratified by site.",
       [W(f"{H}/NCT01394952/Prot_000.pdf", "will be randomized to one of 2 treatment groups (1.5 mg dulaglutide or placebo) following a 1:1 ratio", "using an IVRS.")]),
   "D2_deviations_assignment": ("low", "Double-blind treatment period; primary analyses by intent-to-treat.",
       [W(f"{H}/NCT01394952/Prot_000.pdf", "The run-in period is single-blind and the treatment period is double-blind.", "double-blind."),
        W(f"{H}/NCT01394952/Prot_000.pdf", "The primary analyses will be based on the intent-to-treat principle", "Cox proportional hazards regression model.")]),
   "D3_missing_outcome_data": ("some_concerns", "Only the protocol's REQUIREMENT to ascertain vital status is held; the achieved completeness is not (results paper not held, registry flow not rendered). 3.1 = NI.",
       [W(f"{H}/NCT01394952/Prot_000.pdf", "At a minimum, vital status must be ascertained for all randomized study participants.", "all randomized study participants.")]),
   "D4_outcome_measurement": ("low", "Independent CEC adjudicates all primary endpoint events; the trial is double-blind (assessors' awareness: 4.3 = PN). Blinding of the CEC is not stated verbatim in held text -- flagged for review.",
       [W(f"{H}/NCT01394952/Prot_000.pdf", "An independent CEC will adjudicate all primary endpoint events.", "all primary endpoint events.")]),
   "D5_selection_of_reported_result": ("low", "SAP version 1 approved 21 Nov 2011 before the first unblinding; the protocol fixes the 3-point composite as the primary efficacy measure.",
       [W(f"{H}/NCT01394952/SAP_001.pdf", "Version 1 of this SAP was approved on 21 November 2011 prior to the first unblinding", "treatment codes."),
        W(f"{H}/NCT01394952/Prot_000.pdf", "The primary efficacy measure is the time to first occurrence of the composite endpoint", "(adjudicated as such).")])}},
 "HARMONY Outcomes": {"pmid": "30291013", "nct": "NCT02465515", "domains": {
   "D1_randomisation": ("low", "Sequestered, fixed randomisation schedule (concealed), matching placebo, 1:1.",
       [W(f"{H}/30291013/enlighten_170787.pdf", "Patients were assigned in a 1:1 ratio to receive subcutaneous injections of albiglutide", "randomisation schedule.")]),
   "D2_deviations_assignment": ("low", "All randomised patients analysed whether or not treatment was taken (ITT), matching placebo.",
       [W(f"{H}/30291013/enlighten_170787.pdf", "These analyses included all patients randomly assigned to study", "status could be ascertained).")]),
   "D3_missing_outcome_data": ("low", "Vital status unknown for 61 of 9463 (0.6%).",
       [W(f"{H}/30291013/enlighten_170787.pdf", "Vital status was not known for 61 of 9463 participants (0.6%)", "1).")]),
   "D4_outcome_measurement": ("low", "Independent clinical events classification committee unaware of trial-group assignments.",
       [W(f"{H}/30291013/enlighten_170787.pdf", "An independent clinical events classification committee whose members were", "primary 211 composite outcome")]),
   "D5_selection_of_reported_result": ("low", "The Reporting and Analysis Plan (based on protocol amendment 3, 04-Apr-2017) specifies time to first MACE as the primary analysis, before database freeze.",
       [W(f"{H}/NCT02465515/SAP_001.pdf", "This RAP is based on protocol amendment 3 (Dated: 04-APR-2017)", "(Dated: 04-APR-2017)"),
        W(f"{H}/NCT02465515/SAP_001.pdf", "Time to first occurrence of MACE (cardiovascular death, myocardial infarction, or stroke)", "The primary analysis will be non-inferiority.")])},
   "D2_treatment_discontinuation": ("24% vs 27% discontinued study medication prematurely (not death)",
       [W(f"{H}/30291013/enlighten_170787.pdf", "A total of 24% of patients assigned to albiglutide and 27% of patients assigned to placebo", "other than death.")])},
 "EXSCEL": {"pmid": "28910237", "nct": "NCT01144338", "domains": {
   "D1_randomisation": ("low", "IVRS, computer-generated block randomisation within site, stratified; groups did not differ at baseline.",
       [W(f"{H}/PMC9792409/efetch.xml", "An interactive voice-response system assigned patients on the basis of computer-generated block randomization", "history of cardiovascular disease."),
        W(f"{H}/PMC9792409/efetch.xml", "The demographic, disease, and clinical characteristics of the patients did not differ significantly between the groups", "between the groups")]),
   "D2_deviations_assignment": ("low", "Double-blind, matching placebo; Cox analyses in the intention-to-treat population.",
       [W(f"{H}/PMC9792409/efetch.xml", "We conducted this pragmatic, randomized, double-blind, placebo-controlled, event-driven trial", "35 countries."),
        W(f"{H}/PMC9792409/efetch.xml", "The time-to-event analyses were performed with the use of a Cox proportional-hazards model", "intention-to-treat population")]),
   "D3_missing_outcome_data": ("low", "96.2% completed; vital status obtained for 98.8%, including searches of health records for those lost or withdrawn.",
       [W(f"{H}/PMC9792409/efetch.xml", "A total of 14,187 patients (96.2%) completed the trial, and vital status was obtained for 98.8%", "98.8% of the patients.")]),
   "D4_outcome_measurement": ("low", "Independent clinical events classification committee unaware of trial-group assignments.",
       [W(f"{H}/PMC9792409/efetch.xml", "An independent clinical events classification committee whose members were unaware of the trial-group assignments", "primary composite outcome")]),
   "D5_selection_of_reported_result": ("low", "Design paper (published before unblinding) fixes the primary CV composite and the ITT superiority analysis; SAP amendments (2016/2017, during blinded closeout) changed the event window -- noted for the reviewer.",
       [W(f"{H}/SPIRAL_exscel/design.pdf", "The primary efficacy hypothesis of superiority will be assessed by a superiority analysis in the intent-to-treat (ITT) population.", "(ITT) population.")])},
   "D2_treatment_discontinuation": ("premature discontinuation of the regimen, driven by patient decision, was a major limitation",
       [W(f"{H}/PMC9792409/efetch.xml", "A major limitation of our trial was the rate of premature discontinuation of the trial regimen", "by patient decision.")])},
 "FLOW": {"pmid": "38785209", "nct": "NCT03819153", "domains": {
   "D1_randomisation": ("low", "Central IWRS 1:1 with visually identical placebo, stratified by SGLT2i use; no major baseline imbalances.",
       [W(f"{H}/PMC10469096/fullText.xml", "Participants were randomly assigned 1:1, using a central interactive web response system", "visually identical placebo"),
        W(f"{H}/PMC11485243/fullText.xml", "There were no major imbalances between groups for baseline participant characteristics", "baseline participant characteristics")]),
   "D2_deviations_assignment": ("low", "Participants, investigators and trial personnel blinded; ITT estimand (irrespective of adherence), FAS = all randomised as assigned.",
       [W(f"{H}/PMC10469096/fullText.xml", "Participants, investigators and all trial personnel", "blinded to treatment assignment."),
        W(f"{H}/NCT03819153/SAP_001.pdf", "The estimand for all objectives is an intention-to-treat estimand", "changes to background medication.")]),
   "D3_missing_outcome_data": ("low", "Vital status known for 98.6%.",
       [W(f"{H}/PMC11931213/fullText.xml", "Vital status was known in 98.6% of participants", "98.6% of participants")]),
   "D4_outcome_measurement": ("low", "External, independent, blinded EAC.",
       [W(f"{H}/NCT03819153/Prot_000.pdf", "These events are reviewed by an independent external event adjudication committee (EAC) in a blinded manner", "in a blinded manner")]),
   "D5_selection_of_reported_result": ("low", "Design paper (Jan 2023, before the Oct 2023 stop) and SAP v1.0 (07-Apr-2019) name 3-point MACE a confirmatory secondary endpoint analysed by stratified Cox.",
       [W(f"{H}/PMC10469096/fullText.xml", "Confirmatory secondary endpoints are annual rate of change of eGFR", "three-point MACE"),
        W(f"{H}/NCT03819153/SAP_001.pdf", "SAP version 1.0 dated 07-APR-2019", "07-APR-2019"),
        W(f"{H}/NCT03819153/SAP_001.pdf", "The confirmatory secondary time-to-event endpoints are analysed using the stratified Cox proportional hazards model", "for the primary endpoint.")])},
   "D2_treatment_discontinuation": ("permanent discontinuation 28.8% (pooled); protocol keeps discontinuers in follow-up",
       [W(f"{H}/PMC11485243/fullText.xml", "permanent discontinuation of randomized treatment was reported in 28.8%", "28.8%")])},
 "ELIXA": {"pmid": "26630143", "nct": "NCT01147250", "domains": {
   "D1_randomisation": ("some_concerns", "Randomised via IVRS (incidental mention) with similar baseline characteristics, but no held source describes sequence generation or concealment beyond that (1.1 = NI).",
       [W(f"{H}/FDA_208471/MedR.pdf", "The demographic and baseline characteristics were generally similar between treatment groups for the ITT population.", "for the ITT population.")]),
   "D2_deviations_assignment": ("low", "Double-blind; MACE analyses in the ITT, all-as-randomised population.",
       [W(f"{H}/FDA_208471/MedR.pdf", "ELIXA was a double-blind, randomized (1:1), parallel design trial", "standard of care"),
        W(f"{H}/FDA_208471/MedR.pdf", "The CV analyses for MACE events were based on the intent-to-treat (ITT), all patients as randomized population.", "all patients as randomized population.")]),
   "D3_missing_outcome_data": ("low", "Vital status available for 99%; 71 lacked vital-status follow-up (42 placebo vs 29 lixisenatide).",
       [W(STATR_ELIXA, "Vital status was available for 99% of the randomized subjects", "29 in the lixisenatide group.")]),
   "D4_outcome_measurement": ("low", "Cardiovascular adjudication committee blinded to treatment assignment.",
       [W(f"{H}/FDA_208471/MedR.pdf", "These cardiovascular events were adjudicated by a cardiovascular adjudication committee (CAC) blinded to treatment assignment.", "blinded to treatment assignment.")]),
   "D5_selection_of_reported_result": ("some_concerns", "The FDA reviews DISAGREE on the status of the 3-point result: the statistical review lists 'time to first secondary MACE event' as a secondary endpoint with a 'pre-specified' Cox analysis, the summary review calls it a sensitivity analysis, and the registry lists it as neither; no dated SAP is held.",
       [W(STATR_ELIXA, "In addition to the primary MACE+ endpoint, two secondary endpoints", "were also evaluated."),
        W(f"{H}/FDA_208471/SumR.pdf", "Sensitivity analyses relying on the three component MACE endpoint", "results of the primary analysis.")])},
   "D2_treatment_discontinuation": ("more discontinued lixisenatide early; exposures overall balanced",
       [W(f"{H}/FDA_208471/MedR.pdf", "While more subjects discontinued in the lixisenatide arms earlier in the study", "exposures were overall balanced.")])},
}


def main():
    spec = {"trials": {}}
    for trial, t in T.items():
        doms = {}
        for dom, (level, why, ws) in t["domains"].items():
            doms[dom] = {"proposal": level, "why": why,
                         "witnesses": [{k: v for k, v in w.items() if not k.startswith("_")} for w in ws]}
        entry = {"pmid": t["pmid"], "nct": t["nct"], "domains": doms}
        if t.get("D2_treatment_discontinuation"):
            why, ws = t["D2_treatment_discontinuation"]
            entry["D2_treatment_discontinuation"] = {"why": why, "witnesses": [{k: v for k, v in w.items() if not k.startswith("_")} for w in ws]}
        spec["trials"][trial] = entry
    json.dump(spec, open(os.path.join(os.path.dirname(__file__), "SPEC.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print("SPEC written:", len(spec["trials"]), "trials")


if __name__ == "__main__":
    main()
