"""SGLT2 HHF-in-CVOTs (sglt2-primary-prevention-hf) fixtures, 2026-09-28. Every span is asserted against held bytes first.
 (1) PROGRAMME vs TRIALS: the CANVAS Program's one result combines CANVAS (NCT01032629) + CANVAS-R (NCT01989754). It is a
     PROGRAMME (docs/programmes.json): one programme-level input representing two trials, its eligibility DERIVED from each
     constituent's own held registry rows. The pool keeps 4 inputs representing 5 trials, never the combined estimate
     alongside a constituent's. The family ledger's 'contributing without structural eligibility' is reconciled from
     source witnesses: DECLARE's entry population (its registry condition reads 'Diabetes Mellitus, Non-Insulin-Dependent';
     its inclusion criterion and enrolment sentence say type 2 diabetes) and EMPA-REG OUTCOME's randomised contrast (the
     registry names the drug by its code, BI 10773, in double-dummy arms; its own title and the report's randomisation
     sentence say empagliflozin vs placebo).
 (2) EMPA-REG OUTCOME Table 2 (patients; at least one dose; on treatment + 7 days) -- any AE 4,230/4,687 vs 2,139/2,333;
     events consistent with genital infection 301 vs 42; diabetic ketoacidosis 4 vs 1 -- is NOT held: NEJM PDF 403, the
     repository copy 403, Europe PMC not open access (ATTEMPTS.jsonl). The values are RELAYED (docs/relayed_values.json),
     never admitted; the source's own aggregate categories are named, and the registry's coded preferred terms are never
     summed into them. The genital-infection refusal carried DECLARE's reason (a copy error): rewritten for EMPA-REG.
 (3) DECLARE's genital-infection refusal stays: its reported outcome is genital infections leading to discontinuation or
     serious -- a narrower outcome than all genital infections.
  PYTHONPATH=. python outputs/handover/sglt2_sources/make_sglt2_hhf_fixtures.py"""
import hashlib, json, os, re

SLUG = "sglt2-primary-prevention-hf"
H = "evidence/acquisition_cascade/held"
REC = f"cache/{SLUG}/records.json"
BY = "evidence lane (Claude Opus 5.5), 2026-09-28, source-backed"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
AE, GEN, DKA = "Adverse events", "Genital infection", "Diabetic ketoacidosis"


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"\{\n( +)\"", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


def held(path, span, where):
    n = flat(open(path, encoding="utf-8").read()).count(flat(span))
    assert n >= 1, f"{where}: {span!r} not in {path}"
    return span


recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}
for pid in ("28605608", "26378978", "30415602"):
    assert pid in recs, f"{pid} not in {REC}"

# ------------------------------------------------------------------ (1a) the CANVAS Program: a PROGRAMME of two trials
CV_INT = held(REC, "The CANVAS Program integrated data from two trials involving a total of 10,142 participants with type 2 "
                   "diabetes and high cardiovascular risk.", "CANVAS programme sentence")
CV_ARMS = held(REC, "Participants in each trial were randomly assigned to receive canagliflozin or placebo", "CANVAS arms")
CV_IDS = held(REC, "CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754", "CANVAS registrations")
R_CV, R_CVR = f"{H}/CANVAS-registration/NCT01032629.json", f"{H}/CANVAS-R-registration/NCT01989754.json"
for p, acr in ((R_CV, "CANVAS"), (R_CVR, "CANVAS-R")):
    assert json.load(open(p, encoding="utf-8"))["protocolSection"]["identificationModule"].get("acronym") == acr, p
CV_T = held(R_CV, "CANVAS - CANagliflozin cardioVascular Assessment Study", "CANVAS registration title")
CVR_T = held(R_CVR, "A Study of the Effects of Canagliflozin (JNJ-28431754) on Renal Endpoints in Adult Participants With "
                    "Type 2 Diabetes Mellitus", "CANVAS-R registration title")
pp = "docs/programmes.json"
pg = json.load(open(pp, encoding="utf-8")) if os.path.exists(pp) else {
    "_doc": ("PROGRAMMES (harness/trial_family.programme_declaration): one effect estimated across several registered trials. "
             "A programme is ONE analysis input representing its constituents; its eligibility is derived by screening each "
             "constituent on its own held registry rows; a pool never holds the programme alongside a constituent "
             "(PROGRAMME_WITH_CONSTITUENT, blocking). Witnesses are re-verified against held bytes."),
    "topics": {}}
pg["topics"][SLUG] = [{
    "programme_id": "CANVAS-Program", "label": "CANVAS Program", "report_id": "28605608",
    "constituents": ["NCT01032629", "NCT01989754"],
    "basis": ("the report integrates two randomised trials into one result and names both registrations; each constituent "
              "is its own registered trial (CANVAS, CANVAS-R), so the report is neither one trial's report nor an alias "
              "bridge between them"),
    "decided_by": BY,
    "witnesses": [{"kind": "report: programme integration sentence", "witness": W(REC, CV_INT)},
                  {"kind": "report: per-trial randomisation", "witness": W(REC, CV_ARMS)},
                  {"kind": "report: constituent registrations", "witness": W(REC, CV_IDS)},
                  {"kind": "registry: constituent 1 (CANVAS)", "witness": W(R_CV, CV_T)},
                  {"kind": "registry: constituent 2 (CANVAS-R)", "witness": W(R_CVR, CVR_T)}]}]
dump(pp, pg)

# ------------------------------------------------------------------ (1b) EMPA-REG OUTCOME: the contrast from witnesses
R_ER = f"{H}/EMPA-REG-OUTCOME-registration/NCT01131676.json"
ER_T = held(R_ER, "BI 10773 (Empagliflozin) Cardiovascular Outcome Event Trial in Type 2 Diabetes Mellitus Patients "
                  "(EMPA-REG OUTCOME).", "registry title names the code")
ER_P = held(R_ER, "Placebo tablets matching BI 10773", "placebo arm")
ER_R = held(REC, "We randomly assigned patients to receive 10 mg or 25 mg of empagliflozin or placebo once daily.",
            "report randomisation sentence")
cp = "docs/contrast_witnesses.json"
cw = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {
    "_doc": ("Randomised contrasts the held registry rows cannot DERIVE (harness/trial_family.source_witness), ESTABLISHED from "
             "source witnesses, each re-verified; only ESTABLISHED admits."),
    "topics": {}}
cw["topics"].setdefault(SLUG, {})["NCT01131676"] = {
    "state": "ESTABLISHED",
    "contrast": {"drug": "empagliflozin (registry code BI 10773), 10 mg and 25 mg", "comparator": "placebo",
                 "design": "double-dummy: every registry arm lists a 'Placebo BI 10773' component"},
    "basis": ("the registry names the drug only by its sponsor code in double-dummy arms, so no arm pair is a drug-vs-placebo "
              "contrast BY NAME; the registry's own title equates the code with empagliflozin, its comparator arm is placebo, "
              "and the primary report states the randomisation"),
    "decided_by": BY,
    "witnesses": [{"kind": "registry title (code = drug)", "witness": W(R_ER, ER_T)},
                  {"kind": "registry placebo-comparator arm", "witness": W(R_ER, ER_P)},
                  {"kind": "report randomisation sentence", "witness": W(REC, ER_R)}]}
dump(cp, cw)

# ------------------------------------------------------------------ (1c) DECLARE-TIMI 58: the population from witnesses
R_DC = f"{H}/DECLARE-registration/NCT01730534.json"
DC_I = held(R_DC, "Diagnosed with Type 2 Diabetes", "DECLARE inclusion criterion")
DC_R = held(R_DC, "High Risk for Cardiovascular events", "DECLARE CV-risk criterion")
DC_E = held(REC, "We randomly assigned patients with type 2 diabetes who had or were at risk for atherosclerotic "
                 "cardiovascular disease to receive either dapagliflozin or placebo.", "DECLARE enrolment sentence")
pwp = "docs/population_witnesses.json"
pw = json.load(open(pwp, encoding="utf-8"))
pw["topics"].setdefault(SLUG, {})["NCT01730534"] = {
    "state": "ESTABLISHED",
    "basis": ("the protocol's population (type 2 diabetes at cardiovascular risk) is stated by the registry's INCLUSION "
              "criteria and the primary report's enrolment sentence; the registry condition label 'Diabetes Mellitus, "
              "Non-Insulin-Dependent' is an older MeSH synonym, not a different population"),
    "decided_by": BY,
    "witnesses": [{"kind": "registry inclusion criterion", "witness": W(R_DC, DC_I)},
                  {"kind": "registry inclusion criterion", "witness": W(R_DC, DC_R)},
                  {"kind": "primary report enrolment sentence", "witness": W(REC, DC_E)}]}
dump(pwp, pw)

# ------------------------------------------------------------------ (2) EMPA-REG Table 2: relayed, typed, never summed
ER_SIG = held(REC, "Among patients receiving empagliflozin, there was an increased rate of genital infection but no increase "
                   "in other adverse events.", "EMPA-REG abstract safety sentence")
NOT_HELD = ("EMPA-REG OUTCOME's Table 2 (NEJM 2015) is not held: the NEJM PDF and the repository copy returned 403 and Europe "
            "PMC holds no open-access copy (evidence/acquisition_cascade/ATTEMPTS.jsonl)")
ve_p = f"cache/{SLUG}/verified_effects.json"
ve = json.load(open(ve_p, encoding="utf-8"))
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])
prior = {r.get("outcome"): r for r in as_list(ve.get("26378978"))}
assert prior.get(DKA, {}).get("source_span"), "EMPA-REG's DKA refusal must keep its registry span"
rows = [r for r in as_list(ve.get("26378978")) if r.get("outcome") not in (AE, GEN, DKA)]
rows += [
    {"outcome": AE, "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE", "override": True, "source_level": 1,
     "document_ref": REC, "source_span": ER_SIG, "reported_unresolved_span": ER_SIG,
     "reason": (f"The report states its adverse events as an aggregate (Table 2, patients with any adverse event, at least one "
                f"dose, on treatment + 7 days); {NOT_HELD}. The value is relayed, not admitted. The registry's serious and "
                f"other adverse-event rows are separate, possibly overlapping sets and are never summed into it.")},
    {"outcome": GEN, "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE", "override": True, "source_level": 1,
     "document_ref": REC, "source_span": ER_SIG, "reported_unresolved_span": ER_SIG,
     "reason": (f"The report states genital infection as its own aggregate category (Table 2: events consistent with genital "
                f"infection, patients); {NOT_HELD}. The value is relayed, not admitted. The registry's sex-specific and "
                f"preferred-term rows are never summed into the category.")},
    {**prior[DKA],   # its registry span, document and candidate rows are kept; only the reason is corrected
     # the held registry rows REPORT ketoacidosis for this trial (a different, coded definition): the outcome is reported
     # and unresolved, never 'not reported' -- only the abstract of the paper is held
     "reported_unresolved_span": prior[DKA]["source_span"],
     "reason": (f"The report's Table 2 carries diabetic ketoacidosis as its own row; {NOT_HELD}, and the held abstract does "
                f"not state it. The value is relayed, not admitted. The registry separates diabetic, unspecified and related "
                f"ketoacidosis preferred terms: a different definition, never summed into the report's row.")}]
ve["26378978"] = rows
dump(ve_p, ve)

rp = "docs/relayed_values.json"
rvd = json.load(open(rp, encoding="utf-8"))
rvd["values"] = [v for v in rvd["values"] if not (v["topic"] == SLUG and v["trial"] == "PMID 26378978")]
for outcome, value in (
        (AE, "any adverse event 4,230/4,687 empagliflozin (pooled doses) vs 2,139/2,333 placebo (patients)"),
        (GEN, "events consistent with genital infection 301/4,687 vs 42/2,333 (patients; the source's own aggregate category)"),
        (DKA, "diabetic ketoacidosis 4/4,687 vs 1/2,333 (patients)")):
    rvd["values"].append({
        "topic": SLUG, "trial": "PMID 26378978", "outcome": outcome, "value": value,
        "relayed_by": "the orchestrating lane (SGLT2 HHF-in-CVOTs review fixtures, 2026-09-28)",
        "said_to_be_in": ("EMPA-REG OUTCOME, NEJM 2015, Table 2: patients who received at least one dose; events on "
                          "treatment + 7 days"),
        "why_not_held": NOT_HELD,
        "not_for": ["a sum of the registry's coded preferred terms", "an as-randomised denominator"]})
dump(rp, rvd)

# ------------------------------------------------------------------ (3) DECLARE: the narrower genital outcome stays refused
DC_GEN = held(REC, "genital infections that led to discontinuation of the regimen or that were considered to be serious "
                   "adverse events (0.9% vs. 0.1%, P<0.001)", "DECLARE genital outcome")
g = [r for r in as_list(ve.get("30415602")) if r.get("outcome") == GEN]
assert len(g) == 1 and g[0].get("provenance") == "REFUSED_ON_EVIDENCE" and DC_GEN in g[0].get("source_span", ""), \
    "DECLARE's genital-infection refusal must stay, witnessed by its serious/discontinuation outcome"
print("SGLT2 HHF-in-CVOTs fixtures written")
