"""Finerenone (CKD + T2D) review fixtures, 2026-09-27. Every span is cut from held bytes (or asserted in them) first.
 (2) SCREENING GAPS, both absent from the inventory:
     FIVE-STAR (NCT05887817; PMID 41351003, Cardiovasc Diabetol 2025-12-05, CC BY): double-blind, placebo-controlled,
       102 randomised, primary CAVI at week 24 -- a mechanistic trial, eligible on PICO/design; its surrogate is never
       relabelled as an event HR. Registry status UNKNOWN (last verified 2024-02), completion ESTIMATED: the publication
       outranks the stale registry status.
     CONFIDENCE (NCT05254002): 3-arm double-dummy; comparisons per ARM PAIR (harness.arm_pairs): A vs C (finerenone vs
       placebo on empagliflozin) eligible; B vs C (finerenone vs empagliflozin) and A vs B (empagliflozin vs placebo on
       finerenone) are not.
 (3) FIDELITY (PMID 35023547): the prespecified IPD pool of FIDELIO-DKD + FIGARO-DKD -- a pooled report of two existing
     families, NEVER a third trial and never imported (>=57% HR 0.77 (0.67-0.88); >=40% HR 0.85 (0.77-0.93)).
  PYTHONPATH=. python outputs/handover/finerenone_sources/make_finerenone_fixtures.py"""
import hashlib, json, os, re, html

from harness.report_family import _witness_text

H = "evidence/acquisition_cascade/held/"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def W(path, span):
    w = {"path": path, "sha256": sha(path), "span": span}
    assert " ".join(span.split()) in " ".join(_witness_text(".", w).split()), (path, span[:90])
    return w


def reg_title(p):
    return json.load(open(p, encoding="utf-8"))["protocolSection"]["identificationModule"]["officialTitle"]


# ------------------------------------------------------------------------------------------- CONFIDENCE arm pairs
CONF = H + "CONFIDENCE/NCT05254002.json"
A, B, C = "Finerenone and Empagliflozin", "Finerenone and Empagliflozin placebo", "Empagliflozin and Finerenone placebo"
labels = [a["label"] for a in json.load(open(CONF, encoding="utf-8"))["protocolSection"]["armsInterventionsModule"]["armGroups"]]
assert labels == [A, B, C], labels
POP = W(CONF, "in Participants With Chronic Kidney Disease and Type 2 Diabetes")
DESIGN = W(CONF, "Phase 2, Double-blind, Three-arm Study")


def pair(cid, ex, cp, **kw):
    return {"comparison_id": cid, "kind": "ARM_PAIR", "reports": ["NCT05254002"], "population": {"witness": POP},
            "design": {"witness": DESIGN}, "arm_pair": {"experimental": {"witness": W(CONF, ex)}, "comparator": {"witness": W(CONF, cp)}},
            "comparator": {"witness": W(CONF, cp)}, **kw}


conf_fam = {
    "family_id": "NCT05254002", "registration": "NCT05254002", "label": "CONFIDENCE", "kind": "ARM_PAIRS",
    "registration_conditions_note": "3-arm double-dummy: each comparison is a pair of arms judged on what the two arms differ in",
    "comparisons": [
        pair("CONFIDENCE:A-vs-C finerenone+empagliflozin vs empagliflozin+finerenone-placebo", A, C,
             result={"state": "PUBLISHED_NO_TARGET_OUTCOME", "basis": (
                 "registry results posted: primary UACR ratio at day 180 (a surrogate, never relabelled as an event HR); "
                 "the kidney composite is not an outcome measure")},
             harm_candidates=[{"outcome": "Hyperkalemia", "state": "EXTRACTED_NOT_ADMITTED",
                               "values": {"ai": 25, "n1i": 268, "ci": 10, "n2i": 266},
                               "what": ("posted adverse events, MedDRA term 'Hyperkalaemia', non-serious rows (no serious "
                                        "hyperkalaemia row is posted), safety set: Finerenone + Empagliflozin 25/268 vs "
                                        "Empagliflozin 10/266; the term only, not 'blood potassium increased'"),
                               "source": {"path": CONF, "sha256": sha(CONF)},
                               "not_admitted_because": "CONFIDENCE is not yet in the inventory; admission is a served-number change"}]),
        pair("CONFIDENCE:B-vs-C finerenone+empagliflozin-placebo vs empagliflozin+finerenone-placebo", B, C),
        pair("CONFIDENCE:A-vs-B finerenone+empagliflozin vs finerenone+empagliflozin-placebo", A, B)],
}
cp_ = "docs/comparison_families.json"
cf = json.load(open(cp_, encoding="utf-8"))
cf["families"] = [f for f in cf["families"] if f["family_id"] != conf_fam["family_id"]] + [conf_fam]
open(cp_, "w", encoding="utf-8", newline="\n").write(json.dumps(cf, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------- FIDELITY pooled report
FREC = H + "FIDELITY/europepmc_record_35023547.json"
FXML = H + "FIDELITY/PMC8830527.xml"                     # CC BY-NC: held locally only
EX = "evidence/acquisition_cascade/excerpts/FIDELITY_eGFR40_kidney_composite_sentence.txt"
fx = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", open(FXML, encoding="utf-8").read())).split())
S40 = ("The composite kidney outcome of kidney failure, sustained ≥40% eGFR decrease, or renal death occurred in 854 (13.1%) "
       "and 995 (15.3%) patients receiving finerenone and placebo, respectively (HR, 0.85; 95% CI, 0.77–0.93; P = 0.0004;")
assert fx.count(S40) == 1
os.makedirs(os.path.dirname(EX), exist_ok=True)
open(EX, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (one verbatim sentence) of a held document that is not redistributed (CC BY-NC 4.0)\n"
    f"# source: FIDELITY, Agarwal et al., Eur Heart J 2022 (PMID 35023547), Europe PMC full text PMC8830527; held sha256 {sha(FXML)}\n\n"
    + S40 + "\n")
FID_REG, FIG_REG = H + "PMID33264825/NCT02540993.json", H + "PMID34449181/NCT02545049.json"
fidelity = {
    "report_id": "PMID 35023547",
    "citation": "Agarwal R et al. Eur Heart J 2022;43:474-484 (FIDELITY: prespecified pooled analysis of FIDELIO-DKD and FIGARO-DKD), DOI 10.1093/eurheartj/ehab777",
    "kind": "POOLED_ANALYSIS_OF_CONSTITUENT_TRIALS",
    "trials": [
        {"label": "FIDELIO-DKD", "registration": "NCT02540993", "reports": ["PMID 33264825"],
         "population": {"witness": W(FID_REG, reg_title(FID_REG))}},
        {"label": "FIGARO-DKD", "registration": "NCT02545049", "reports": ["PMID 34449181"],
         "population": {"witness": W(FIG_REG, reg_title(FIG_REG))}}],
    "combined_analyses": [
        {"label": "FIDELITY", "n": 13026, "policy": "NEVER_IMPORTED",
         "witness": W(FREC, "two phase III, multicentre, double-blind trials involving patients with CKD and type 2 diabetes, randomized 1:1 to finerenone or placebo, were combined")},
        {"label": "FIDELITY kidney composite (>=57% eGFR decrease)", "n": 13026, "policy": "NEVER_IMPORTED",
         "witness": W(FREC, "The composite kidney outcome occurred in 360 (5.5%) patients receiving finerenone and 465 (7.1%) receiving placebo (HR, 0.77; 95% CI, 0.67-0.88; P = 0.0002)")},
        {"label": "FIDELITY kidney composite (>=40% eGFR decrease)", "n": 13026, "policy": "NEVER_IMPORTED",
         "witness": {"path": EX, "sha256": sha(EX), "span": S40}}],
    "full_text_state": "HELD locally (Europe PMC PMC8830527, CC BY-NC 4.0, not redistributed); the >=40% sentence is a committed excerpt",
}
mp = "docs/multi_trial_reports.json"
m = json.load(open(mp, encoding="utf-8"))
m["reports"] = [r for r in m["reports"] if r["report_id"] != fidelity["report_id"]] + [fidelity]
open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")

# ------------------------------------------------------------------------------------------- known-missing entries
FS_REC, FS_XML, FS_REG = H + "FIVE-STAR/europepmc_record_41351003.json", H + "FIVE-STAR/PMC12681115.xml", H + "FIVE-STAR/NCT05887817.json"
W(FS_REC, "Among 102 patients randomised, 101")
W(FS_REC, "two-arm parallel, placebo-controlled, double-blind, randomised clinical trial")
kp = "docs/known_eligible_missing.json"
k = json.load(open(kp, encoding="utf-8"))
k["topics"]["finerenone-ckd-t2d-renal"] = [
    {"trial": "FIVE-STAR", "mechanism": "concept-query", "status": "source_held_published",
     "registration": "NCT05887817", "pmid": "41351003",
     "acquisition": {"route": "acquisition cascade: recorded Europe PMC discovery search, then Europe PMC open-access full text PMC12681115 (CC BY 4.0)",
                     "held_path": FS_XML, "held_sha256": sha(FS_XML)},
     "design": "double-blind, placebo-controlled, two-arm; 102 randomised, 101 analysed; 24 weeks",
     "lifecycle": {"registry_status": "UNKNOWN (last verified 2024-02)", "registry_completion": "2026-07-31 ESTIMATED",
                   "published": "2025-12-05", "note": "the publication outranks the stale registry status: completed and reported"},
     "per_outcome": {"Kidney composite outcome": "PUBLISHED_NO_TARGET_OUTCOME (primary CAVI, a surrogate; never relabelled as an event HR)",
                     "Hyperkalemia": "REPORTED_UNRESOLVED (the full text analyses hyperkalaemia as a safety endpoint; its table is not yet extracted)",
                     "Hyperkalemia-related treatment discontinuation": "REPORTED_UNRESOLVED (not yet extracted)"}},
    {"trial": "CONFIDENCE", "mechanism": "concept-query", "status": "source_held_arm_pairs_declared",
     "registration": "NCT05254002",
     "acquisition": {"route": "acquisition cascade: ClinicalTrials.gov registration + posted results", "held_path": CONF, "held_sha256": sha(CONF)},
     "design": "phase 2, double-blind (quadruple), 3-arm double-dummy; 1,664 randomised; completed 2025-03-17 (ACTUAL)",
     "comparisons": "A vs C eligible (finerenone vs placebo on empagliflozin); B vs C and A vs B not (docs/comparison_families.json)",
     "per_outcome": {"Kidney composite outcome": "PUBLISHED_NO_TARGET_OUTCOME (UACR, a surrogate)",
                     "Hyperkalemia": "EXTRACTED_NOT_ADMITTED (A vs C 25/268 vs 10/266, registry non-serious 'Hyperkalaemia' term rows)",
                     "Hyperkalemia-related treatment discontinuation": "RETRIEVED_NOT_REPORTED (registry results: not an outcome measure)"}},
]
open(kp, "w", encoding="utf-8", newline="\n").write(json.dumps(k, indent=1, ensure_ascii=False) + "\n")
print("wrote CONFIDENCE arm pairs, FIDELITY pooled report + excerpt, FIVE-STAR / CONFIDENCE known-missing entries")
