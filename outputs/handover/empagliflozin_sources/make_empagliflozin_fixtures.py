"""Empagliflozin-HFpEF review fixtures (2026-09-27). Every span is asserted against held bytes BEFORE anything is written.
  (2) EMPERIAL (Abraham et al., Eur Heart J 2021, DOI 10.1093/eurheartj/ehaa943, PMID 33351892): ONE paper, TWO trials,
      EMPERIAL-Reduced (NCT03448419, N=312) and EMPERIAL-Preserved (NCT03448406, N=315). Both linked; Preserved only is
      relevant to this review. Its safety rows are EXPLORATORY (the protocol prespecifies no harms): serious adverse events
      bound to the trial's own posted registry results; any AE and AE leading to discontinuation are reported in the
      paper's Table 4, which is NOT openly held (Europe PMC: not open access; Unpaywall: no open location) -> REPORTED_UNRESOLVED.
  (3) EMPA-VISION (PMID 37070436, CC BY 4.0; NCT03332212): one registration, two separately randomised cohorts (HFrEF
      17 vs 19, HFpEF 18 vs 18), each judged on its own population; the 72 are never imported as HFpEF.
Also: the per-outcome state of a held, examined registry result (DETERMINE-Preserved and EMPERIAL-Preserved composite).
  python outputs/handover/empagliflozin_sources/make_empagliflozin_fixtures.py"""
import hashlib, json, os

from harness.report_family import _witness_text

ROOT = "."
H = "evidence/acquisition_cascade/held/"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def W(path, span, raw=False):
    """A witness: the span must be in the held file's witness text (JSON: its string values) or, for raw=True, in its
    raw bytes (a JSON number field)."""
    w = {"path": path, "sha256": sha(path), "span": span}
    if raw:
        assert span in open(path, encoding="utf-8").read(), (path, span[:80])
        w["representation"] = "raw bytes"
    else:
        assert span in " ".join(_witness_text(ROOT, w).split()), (path, span[:80])
    return w


EMP_REC = H + "EMPERIAL/europepmc_record_33351892.json"
PRES = H + "NCT03448406/NCT03448406.json"
RED = H + "EMPERIAL-Reduced/NCT03448419.json"
COMPOSITE = "Composite cardiovascular death or worsening heart failure"

pres_reg = json.load(open(PRES, encoding="utf-8"))
oms = [m["title"] for m in pres_reg["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"]]
assert not any("death" in t.lower() or "hospitali" in t.lower() for t in oms), oms
raw = open(PRES, encoding="utf-8").read()
i_pl = raw.index('"id":"EG000","title":"Placebo"')
i_em = raw.index('"id":"EG001","title":"10 mg Empagliflozin"')
SAE_PL = raw[i_pl:raw.index('"seriousNumAtRisk":158', i_pl) + len('"seriousNumAtRisk":158')]
SAE_EM = raw[i_em:raw.index('"seriousNumAtRisk":157', i_em) + len('"seriousNumAtRisk":157')]
assert '"seriousNumAffected":29' in SAE_PL and '"seriousNumAffected":20' in SAE_EM

emperial = {
    "report_id": "PMID 33351892",
    "citation": "Abraham WT et al. Eur Heart J 2021;42:700-710 (EMPERIAL-Reduced and EMPERIAL-Preserved), DOI 10.1093/eurheartj/ehaa943",
    "trials": [
        {"label": "EMPERIAL-Preserved", "registration": "NCT03448406", "n_randomised": 315,
         "population": {"witness": W(PRES, "In Patients With Chronic HeArt FaiLure With Preserved Ejection Fraction (HFpEF) (EMPERIAL - Preserved)")},
         "report_population": {"witness": W(EMP_REC, "preserved EF (>40%, N = 315, EMPERIAL-Preserved)")},
         "registry_results": {
             "state": "SOURCE_HELD_EXAMINED_NOT_ADMITTED", "path": PRES, "sha256": sha(PRES),
             "findings": {"randomised": "157 empagliflozin vs 158 placebo (participant flow STARTED)",
                          "outcome_measures": "; ".join(oms)[:400],
                          "primary_composite_cv_death_or_worsening_hf": "not an outcome measure of this 12-week exercise-capacity trial"},
             "per_outcome": {COMPOSITE: {
                 "state": "RETRIEVED_NOT_REPORTED", "coverage": "REGISTRY_RESULTS (verbatim, posted results) + publication abstract (verbatim); publication full text not held",
                 "basis": "the trial's posted outcome measures are exercise capacity and symptom scores; neither the registry results nor the abstract report cardiovascular death or worsening heart failure"}},
             "exploratory_harms": {
                 "_policy": "EXPLORATORY: the protocol prespecifies no harm outcomes; shown, never pooled, never a served number",
                 "rows": [
                     {"outcome": "Serious adverse events", "state": "EXTRACTED_EXPLORATORY",
                      "values": {"ai": 20, "n1i": 157, "ci": 29, "n2i": 158}, "arm_order": "empagliflozin 10 mg vs placebo",
                      "timeframe": "from first intake of study medication until 7 days after last intake, up to 92 days",
                      "witnesses": [W(PRES, SAE_EM, raw=True), W(PRES, SAE_PL, raw=True)],
                      "note": "the publication's Table 4 reports the same 20/157 vs 29/158 (relayed; Table 4 itself is not held)"},
                     {"outcome": "Any adverse event", "state": "REPORTED_UNRESOLVED",
                      "relayed_values": "79/157 vs 93/158 (Table 4, relayed by the orchestrating lane)",
                      "why": "reported in the paper's Table 4; not openly held (Europe PMC: not open access; Unpaywall: no open location); the registry lists no non-serious events above its 5% threshold, so it cannot give an any-AE count"},
                     {"outcome": "Adverse event leading to discontinuation", "state": "REPORTED_UNRESOLVED",
                      "relayed_values": "9/157 vs 8/158 (Table 4, relayed)",
                      "why": "reported in the paper's Table 4; not openly held; not a field of the posted registry results"}]}}},
        {"label": "EMPERIAL-Reduced", "registration": "NCT03448419", "n_randomised": 312,
         "population": {"witness": W(RED, "In Patients With Chronic HeArt FaiLure With Reduced Ejection Fraction (HFrEF) (EMPERIAL-reduced)")},
         "report_population": {"witness": W(EMP_REC, "reduced EF (HFrEF) (≤40%, N = 312, EMPERIAL-Reduced)")}}],
    "combined_analyses": [],
    "full_text_state": ("NOT_HELD: Europe PMC reports the article not open access (no PMCID); Unpaywall lists no open "
                        "location. Table 4 (safety) is therefore not held; Preserved's serious adverse events are bound to "
                        "its own posted registry results instead."),
}

mp = "docs/multi_trial_reports.json"
m = json.load(open(mp, encoding="utf-8"))
m["reports"] = [r for r in m["reports"] if r["report_id"] != emperial["report_id"]] + [emperial]
for r in m["reports"]:
    for t in r["trials"]:
        if t.get("registration") == "NCT03877224" and t.get("registry_results"):
            t["registry_results"]["per_outcome"] = {COMPOSITE: {
                "state": "RETRIEVED_NOT_REPORTED", "coverage": "REGISTRY_RESULTS (verbatim, posted results) + publication abstract (verbatim)",
                "basis": "a 16-week trial whose posted outcome measures do not include cardiovascular death or worsening heart failure"}}
m["_doc"] = m["_doc"].split(" EMPERIAL")[0] + (" EMPERIAL (empagliflozin HFpEF review) added 2026-09-27: registry_results.per_outcome "
                                                 "states what a held, examined registry result says for a named outcome; "
                                                 "exploratory_harms are shown, never pooled.")
open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- EMPA-VISION: two separately randomised cohorts
EV = H + "EMPA-VISION/PMC10212585.xml"
EVR = H + "EMPA-VISION-registration/NCT03332212.json"
ARMS = ("randomly assigned to empagliflozin (10 mg; n=35: 17 HFrEF and 18 HFpEF) or placebo (n=37: 19 HFrEF and 18 HFpEF) "
        "once daily for 12 weeks")
fam = {
    "family_id": "NCT03332212", "registration": "NCT03332212", "label": "EMPA-VISION", "kind": "COHORTS",
    "registration_conditions_note": "the registration enrols two cohorts (HFrEF, HFpEF) randomised separately within cohort; its conditions describe both",
    "randomisation": {"witness": W(EV, "Patients were stratified into respective cohorts (HFrEF versus HFpEF) and randomly assigned")},
    "whole_trial": {"n": 72, "policy": "NEVER_IMPORTED_AS_EITHER_COHORT",
                    "witness": W(EV, "mechanistic trial that enrolled 72 symptomatic patients")},
    "comparisons": [
        {"comparison_id": "EMPA-VISION:HFpEF-cohort", "kind": "RANDOMISED_COHORT", "reports": ["PMID 37070436"],
         "population": {"witness": W(EV, "HF with preserved ejection fraction (HFpEF; n=36; left ventricular ejection fraction ≥50%")},
         "intervention": {"witness": W(EV, ARMS)},
         "comparator": {"witness": W(EV, "or placebo (n=37: 19 HFrEF and 18 HFpEF)")},
         "arms": {"empagliflozin": 18, "placebo": 18, "witness": W(EV, ARMS)},
         "result": {"state": "PUBLISHED_NO_TARGET_OUTCOME",
                    "basis": "a mechanistic trial: primary end point cardiac PCr/ATP at 12 weeks; no cardiovascular death or worsening heart failure outcome"}},
        {"comparison_id": "EMPA-VISION:HFrEF-cohort", "kind": "RANDOMISED_COHORT", "reports": ["PMID 37070436"],
         "population": {"witness": W(EV, "chronic HF with reduced ejection fraction (HFrEF; n=36; left ventricular ejection fraction ≤40%")},
         "intervention": {"witness": W(EV, ARMS)},
         "comparator": {"witness": W(EV, "or placebo (n=37: 19 HFrEF and 18 HFpEF)")},
         "arms": {"empagliflozin": 17, "placebo": 19, "witness": W(EV, ARMS)}}],
    "registration_witness": W(EVR, "EMPA-VISION: A Randomised, Double-blind, Placebo-controlled, Mechanistic Cardiac Magnetic Resonance Study"),
}
cp = "docs/comparison_families.json"
c = json.load(open(cp, encoding="utf-8"))
c["families"] = [f for f in c["families"] if f["family_id"] != fam["family_id"]] + [fam]
open(cp, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=1, ensure_ascii=False) + "\n")

kp = "docs/known_eligible_missing.json"
k = json.load(open(kp, encoding="utf-8"))
k["topics"]["empagliflozin-hfpef-hosp"] = [{
    "trial": "EMPA-VISION", "mechanism": "concept-query", "status": "source_held_cohorts_declared",
    "note": "one registration, two separately randomised cohorts; the HFpEF cohort is eligible on its own population",
    "pmid": "37070436", "registration": "NCT03332212",
    "acquisition": {"route": "acquisition cascade: Europe PMC open-access full text PMC10212585 (CC BY 4.0) + ClinicalTrials.gov registration",
                    "held_path": EV, "held_sha256": sha(EV)},
    "cohorts": {"HFpEF": "18 empagliflozin vs 18 placebo", "HFrEF": "17 empagliflozin vs 19 placebo",
                "whole_trial": "72, NEVER imported as HFpEF"},
    "target_outcome_state": "PUBLISHED_NO_TARGET_OUTCOME (mechanistic: PCr/ATP)"}]
open(kp, "w", encoding="utf-8", newline="\n").write(json.dumps(k, indent=1, ensure_ascii=False) + "\n")
print("wrote EMPERIAL multi-trial report, DETERMINE per-outcome state, EMPA-VISION cohorts, known-missing entry")
