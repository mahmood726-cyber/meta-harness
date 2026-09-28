"""SGLT2-CKD review fixtures, 2026-09-28. Every span is asserted against held bytes first.
 (1) SOURCE IDENTITY is an executable check (harness/source_identity.py): EMPA-KIDNEY cited as PMC9761906 fails -- its
     own record says PMC7614055 (tests/test_sglt2_fixtures.py).
 (2) SAFETY from the trials' own tables, with SAFETY denominators and each outcome's OWN window (carried per row):
       DAPA-CKD (safety set, at least one dose, 2149 vs 2149): definite or probable DKA 0 vs 2; amputation (surgical or
         spontaneous, excluding trauma) 35 vs 39  -- Glasgow accepted manuscript, CC BY-SA
       CREDENCE (treated, 2200 vs 2197): DKA 11 vs 1 ON-TREATMENT (to 30 days after the last dose); amputation 70 vs 63
         ON-STUDY (to the end of the trial) -- the window differs WITHIN one trial
       EMPA-KIDNEY: 'ketoacidosis' 6 vs 1 including ONE in a participant without diabetes -- a different definition from
         diabetic ketoacidosis: the DKA pool is suppressed across definitions (harness/outcome_restriction.py)
     CREDENCE amputation's refusal is superseded by declaration (scripts/hm3_screening_supersession.py).
 (3) EMPA-KIDNEY long-term follow-up (PMID 39453837, CC BY): the SAME trial; its combined active + post-trial HR 0.79
     (0.72-0.87) is a SEPARATE follow-up policy (no study drug; open-label SGLT2i 43% vs 40%: strategy continuity fails),
     recorded in a version chain whose governing version stays the active trial.
 (4) EMPA-CKD (NCT07060417): a start and a completion both after the source date are never COMPLETED (lifecycle).
 (5) DIAMOND (PMID 32559474, NCT03190694): the publication is linked to its registration; a 53-patient CROSSOVER with a
     proteinuria primary contributes no clinical-event HR, and its sequences are never parallel arms (blocking).
  PYTHONPATH=. python outputs/handover/sglt2_sources/make_sglt2_ckd_fixtures.py"""
import hashlib, html, json, os, re

SLUG = "sglt2-ckd-progression"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
PRIM, DKA, AMP = "Trial-defined primary cardiorenal composite", "Diabetic ketoacidosis", "Lower-limb amputation"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}


def dump(path, data):
    ind = 1
    if os.path.exists(path):
        m = re.match(r"\{\n( +)\"", open(path, encoding="utf-8").read())
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


def once(text, span, where):
    n = flat(text).count(flat(span))
    assert n == 1, f"{where}: {n} occurrences of {span!r}"
    return flat(span)


def local_once(text, pattern, where):
    m = [x.group(0) for x in re.finditer(pattern, flat(text))]
    assert len(m) == 1, f"{where}: {len(m)} matches: {m[:2]}"
    return m[0]


def xml_text(p):
    return flat(html.unescape(re.sub(r"<[^>]+>", " ", open(p, encoding="utf-8").read())))


# ------------------------------------------------------------------ (2) DAPA-CKD, CREDENCE tables
D_PDF, D_TXT = f"{H}/DAPA-CKD/unpaywall.pdf", f"{H}/DAPA-CKD/unpaywall.local.txt"
DT = open(D_TXT, encoding="utf-8").read()
once(DT, "Amputation§ 35/2149 (1.6) — 39/2149 (1.8) — — 0.73", "DAPA-CKD amputation")
once(DT, "Any definite or probable diabetic ketoacidosis 0/2149 — 2/2149 (<0.1) — — 0.50", "DAPA-CKD DKA")
D_AMPDEF = local_once(DT, r"§ Shown are cases of surgical amputation or spontaneous or nonsurgical amputation, excluding amputation due to trauma\.", "DAPA-CKD amputation def")
D_POP = local_once(DT, r"alyses included all the participants who had undergone randomization and received at least one dose of dapagliflozin or placebo\.", "DAPA-CKD safety set")
C_PDF, C_TXT = f"{H}/CREDENCE/unpaywall.pdf", f"{H}/CREDENCE/unpaywall.local.txt"
CT = open(C_TXT, encoding="utf-8").read()
once(CT, "Amputation 70/2200 63/2197 12.3 11.2 1.11 (0.79–1.56) NA", "CREDENCE amputation")
once(CT, "Diabetic ketoacidosis‖ 11/2200 1/2197 2.2 0.2 10.80 (1.39–83.65) NA", "CREDENCE DKA")
C_WIN = local_once(CT, r"We used the data set for all treated patients through 30 days after the last dose for the safety analyses "
                       r"\(on-treatment analysis\) and used the on- ?study analysis that included all treated patients through the "
                       r"end of the trial to evaluate selected adverse events, including cancer, amputation, and fracture\.", "CREDENCE windows")
C_FOOT = local_once(CT, r"‡ The numbers of amputation, fracture, and cancer events were determined in the on-study population, "
                        r"whereas the other safety events were determined in the on-treatment population\.", "CREDENCE footnote")


def tab(name, source, held, rows, notes):
    p = f"{X}/{name}"
    open(p, "w", encoding="utf-8", newline="\n").write(
        f"# EXCERPT of {source}; held locally, not redistributed. Every value is verbatim from our pypdf text of the held "
        "document; the CELL BOUNDARIES are this excerpt's segmentation.\n"
        f"# held: {held} sha256 {sha(held)}\n" + "".join(f"# {n}\n" for n in notes) + "\n=== TABLES (excerpt) ===\n"
        + "\n".join(rows) + "\n")
    return p


DX = tab("DAPA-CKD_Table_safety.tables.txt", "DAPA-CKD (Heerspink et al., NEJM 2020) Table 2, Glasgow accepted manuscript (CC BY-SA)",
         D_PDF, ["TABLE Table 2. Adverse events of interest (safety analysis set)",
                 "Event | Dapagliflozin (N=2149) no./total no. (%) | Placebo (N=2149) no./total no. (%) | P value",
                 "Amputation§ | 35/2149 (1.6) | 39/2149 (1.8) | 0.73",
                 "Any definite or probable diabetic ketoacidosis | 0/2149 | 2/2149 (<0.1) | 0.50"],
         [f"population (verbatim): ...{D_POP}", f"amputation definition (verbatim): {D_AMPDEF}"])
CX = tab("CREDENCE_Table_safety.tables.txt", "CREDENCE (Perkovic et al., NEJM 2019) safety table, Szeged repository copy",
         C_PDF, ["TABLE Safety outcomes (all treated patients)",
                 "Outcome | Canagliflozin no./total no. | Placebo no./total no. | Canagliflozin events/1000 pt-yr | Placebo events/1000 pt-yr | HR (95% CI)",
                 "Amputation | 70/2200 | 63/2197 | 12.3 | 11.2 | 1.11 (0.79–1.56)",
                 "Diabetic ketoacidosis‖ | 11/2200 | 1/2197 | 2.2 | 0.2 | 10.80 (1.39–83.65)"],
         [f"windows (verbatim): {C_WIN}", f"footnote (verbatim): {C_FOOT}"])

as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])
va_p, ve_p = f"cache/{SLUG}/verified_arms.json", f"cache/{SLUG}/verified_effects.json"
va = json.load(open(va_p, encoding="utf-8")) if os.path.exists(va_p) else {}
ve = json.load(open(ve_p, encoding="utf-8"))


def put(store, pid, entry):
    rows = [r for r in as_list(store.get(pid)) if r.get("outcome") != entry["outcome"]] + [entry]
    store[pid] = rows if len(rows) > 1 else rows[0]


def superseded(pid, outcome):
    rows = as_list(ve.get(pid))
    old = next((r for r in rows if r.get("outcome") == outcome), None)
    rest = [r for r in rows if r.get("outcome") != outcome]
    if old:
        if rest:
            ve[pid] = rest if len(rest) > 1 else rest[0]
        else:
            ve.pop(pid, None)
        return {k: old.get(k) for k in ("provenance", "reason") if old.get(k)}
    prev = next((r for r in as_list(va.get(pid)) if r.get("outcome") == outcome), None)
    return (prev or {}).get("supersedes")


ROWS = [
    ("32970396", DKA, 0, 2149, 2, 2149, DX, "Any definite or probable diabetic ketoacidosis | 0/2149 | 2/2149 (<0.1) | 0.50",
     "safety set (at least one dose), 2149 vs 2149", "the trial's safety analysis (as tabulated)",
     "definite or probable diabetic ketoacidosis, adjudicated", "DKA_ADJUDICATED"),
    ("32970396", AMP, 35, 2149, 39, 2149, DX, "Amputation§ | 35/2149 (1.6) | 39/2149 (1.8) | 0.73",
     "safety set (at least one dose), 2149 vs 2149", "the trial's safety analysis (as tabulated)",
     "surgical or spontaneous/nonsurgical amputation, excluding amputation due to trauma", None),
    ("30990260", DKA, 11, 2200, 1, 2197, CX, "Diabetic ketoacidosis‖ | 11/2200 | 1/2197 | 2.2 | 0.2 | 10.80 (1.39–83.65)",
     "treated patients, 2200 vs 2197", "ON-TREATMENT: all treated patients through 30 days after the last dose",
     "diabetic ketoacidosis, confirmed and adjudicated", "DKA_ADJUDICATED"),
    ("30990260", AMP, 70, 2200, 63, 2197, CX, "Amputation | 70/2200 | 63/2197 | 12.3 | 11.2 | 1.11 (0.79–1.56)",
     "treated patients, 2200 vs 2197", "ON-STUDY: all treated patients through the end of the trial",
     "amputation", None)]
for pid, outcome, a, n1, c, n2, t, span, pop, win, defn, key in ROWS:
    sup = superseded(pid, outcome)
    put(va, pid, {"outcome": outcome, "ai": a, "n1i": n1, "ci": c, "n2i": n2, "kind": "extracted_counts",
                  "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
                  "document_ref": t, "document_sha256": sha(t), "source_span": span,
                  "safety_population": pop, "safety_window": win, "harm_definition": defn,
                  **({"harm_definition_key": key} if key else {}), **({"supersedes": sup} if sup else {}),
                  "reason": f"{outcome} from the trial's own table: {a}/{n1} vs {c}/{n2}; {pop}; window {win}."})
dump(va_p, va)
dump(ve_p, ve)

# EMPA-KIDNEY's ketoacidosis: a DIFFERENT definition (it includes a participant without diabetes)
EK_XML = f"{H}/EMPA-KIDNEY/PMC7614055.xml"
EK = xml_text(EK_XML)
EK_KETO = once(EK, "Includes one event of ketoacidosis in a participant without diabetes at baseline", "EMPA-KIDNEY footnote")
# the Europe PMC manuscript is CC BY-ND 4.0: held locally (sha256 in HELD.json, gitignored), never redistributed; the
# witness binds to a committed one-sentence quotation that names the held file's sha256
EK_EXC = "evidence/acquisition_cascade/excerpts/EMPA-KIDNEY_ketoacidosis_footnote.txt"
open(EK_EXC, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (verbatim footnote sentence) of EMPA-KIDNEY (Herrington et al., NEJM 2023), Europe PMC author manuscript "
    "(CC BY-ND 4.0), held locally, not redistributed\n"
    f"# held XML: {EK_XML} sha256 {sha(EK_XML)}\n\n" + EK_KETO + "\n")
op ="docs/outcome_restrictions.json"
orx = json.load(open(op, encoding="utf-8"))
orx["topics"][SLUG] = {DKA: {
    "restriction": "DEFINITION_TYPED",
    "definition": "adjudicated DIABETIC ketoacidosis vs any ketoacidosis (EMPA-KIDNEY counts one in a participant without diabetes)",
    "definitions_by_trial": {"36331190": {"key": "KETOACIDOSIS_ANY_INCL_NONDIABETIC",
                                          "definition": "ketoacidosis, adjudicated, " + EK_KETO,
                                          "witness": W(EK_EXC, EK_KETO)}}}}
dump(op, orx)

# ------------------------------------------------------------------ (3) EMPA-KIDNEY follow-up: a separate policy
FU_XML = f"{H}/EMPA-KIDNEY-followup/PMC7616743.xml"
FU = xml_text(FU_XML)
FU_HR = local_once(FU, r"[^.]{0,200}\(HR=0\.79, 95%CI 0\.72[-–]0\.87\)", "follow-up combined HR") \
    if re.search(r"\(HR=0\.79, 95%CI 0\.72[-–]0\.87\)", FU) else None
if FU_HR is None:
    m = [x.group(0) for x in re.finditer(r"HR=0\.79, 95% ?CI 0\.72[^)]{0,6}0\.87", FU)]
    assert m, "follow-up HR 0.79 (0.72-0.87) not held"
    FU_HR = m[0]
FU_NODRUG = once(FU, "No study drug was issued in the post-trial period, but local doctors could prescribe SGLT2 inhibitors.", "no drug")
FU_OL = local_once(FU, r"During post-trial follow-up, average use was similar between groups \(43% vs\. ?40%\)", "open-label use") \
    if re.search(r"During post-trial follow-up, average use was similar between groups \(43% vs\. ?40%\)", FU) else \
    local_once(FU, r"SGLT2 inhibitor use was similar between groups \(empagliflozin group 43% vs\. [^)]{0,40}\)", "open-label use")
REC = f"cache/{SLUG}/records.json"
recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}
A_SPAN = re.search(r"[^.]*0\.72[^.]*0\.64[^.]*0\.82[^.]*", recs["36331190"]["abstract"]) or \
    re.search(r"hazard ratio, 0\.72; 95% confidence interval \[CI\], 0\.64 to 0\.82", recs["36331190"]["abstract"])
assert A_SPAN, "EMPA-KIDNEY active-trial HR not in the held abstract"
A_SPAN = flat(A_SPAN.group(0))
sp = "docs/source_versions.json"
sv = json.load(open(sp, encoding="utf-8"))
sv["topics"][SLUG] = [{
    "chain_id": "EMPA-KIDNEY:primary:active-vs-post-trial", "trial_id": "PMID 36331190", "outcome": PRIM,
    "versions": [
        {"version_id": "v0-active-trial-2022", "kind": "ORIGINAL", "date": "2022-11-04",
         "source": "NEJM 2023 (PMID 36331190) held abstract", "held": W(REC, A_SPAN),
         "value": {"effect": 0.72, "ci_low": 0.64, "ci_high": 0.82}},
        {"version_id": "v1-long-term-follow-up-2024", "kind": "COMPANION_REPORT", "date": "2024-10-25",
         "source": "Long-term effects of empagliflozin (PMID 39453837, PMC7616743, CC BY): active trial PLUS post-trial",
         "held": W(FU_XML, FU_HR),
         "cells": {"no study drug": FU_NODRUG, "open-label SGLT2 inhibitor use": FU_OL},
         "relation": ("SEPARATE FOLLOW-UP POLICY, not a correction: the post-trial period gave no study drug and open-label "
                      "SGLT2 inhibitors were used 43% vs 40% -- strategy continuity fails, so the combined HR answers a "
                      "different question (assignment policy over active + post-trial time)"),
         "value": {"effect": 0.79, "ci_low": 0.72, "ci_high": 0.87}}],
    "governing": {"state": "DECIDED", "version_id": "v0-active-trial-2022",
                  "reason": ("the review's question is the randomised treatment contrast; the follow-up is the SAME trial "
                             "under a different policy (no study drug, open-label crossover to the class), recorded and shown, "
                             "never a silent replacement of the active-trial result")}}]
dump(sp, sv)
sf_p = "docs/study_families.json"
sf = json.load(open(sf_p, encoding="utf-8"))
sf["topics"][SLUG] = [e for e in sf["topics"].get(SLUG) or [] if e.get("pmid") != "39453837"] + [{
    "pmid": "39453837", "parent": "EMPA-KIDNEY (36331190)", "parent_pmid": "36331190", "publication_role": "long_term_follow_up",
    "kind": ("long-term follow-up of the SAME trial (active + post-trial): a separate follow-up policy (strategy continuity "
             "fails), never a second trial and never a replacement of the active-trial result")}]
dump(sf_p, sf)

# ------------------------------------------------------------------ (5) DIAMOND: linked, crossover, no clinical HR
DREC = f"{H}/DIAMOND/europepmc_record_32559474.json"
dr = json.load(open(DREC, encoding="utf-8"))["resultList"]["result"][0]
DM_DESIGN = "DIAMOND was a randomised, double-blind, placebo-controlled crossover trial done at six hospitals in Canada, Malaysia, and the Netherlands."
DM_N = "53 (mean age 51 years [SD 13]; 32% women) were randomly assigned (27 received dapagliflozin then placebo and 26 received placebo then dapagliflozin)"
assert DM_DESIGN in dr["abstractText"] and DM_N in dr["abstractText"]
rpp = "docs/registry_publications.json"
rpd = json.load(open(rpp, encoding="utf-8"))
st = {"statement": ("a 53-patient CROSSOVER with a proteinuria primary: it contributes no clinical-event hazard ratio, and its "
                    "two SEQUENCES are never read as parallel arms")}
rpd["topics"][SLUG] = [{
    "registration": "NCT03190694", "pmid": "32559474", "label": "DIAMOND (Cherney et al., Lancet Diabetes Endocrinol 2020)",
    "coverage": "ABSTRACT_ONLY (not open access)", "record_witness": W(DREC, DM_DESIGN), "design": "CROSSOVER",
    "identity_check": "53 randomised to two sequences (27 dapagliflozin-then-placebo, 26 placebo-then-dapagliflozin)",
    "per_outcome": {PRIM: st, DKA: st, AMP: st}}]
dump(rpp, rpd)
print("SGLT2-CKD fixtures written")
