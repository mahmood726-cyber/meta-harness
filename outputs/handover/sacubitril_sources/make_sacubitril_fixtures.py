"""Sacubitril-HFrEF review fixtures (2026-09-28). Every span is asserted against held bytes before it is written.
 (1) LIFE (NCT02816736, PMID 34730769): double-blind sacubitril/valsartan vs VALSARTAN (an ARB comparator, eligible by
     protocol C), advanced HFrEF, 24 weeks, principal analysis n=335 (a COVID-related cohort restriction of the 365
     randomised -- NOT all randomised). Absent from the inventory: entered as a KNOWN ELIGIBLE trial. Its CV death or HF
     hospitalisation (48/167 vs 37/168, HR 1.32 (0.86-2.03), eTable 4 of Supplement 2) is REPORTED -- the held main text
     names it and where it is -- but the supplement is NOT held (Europe PMC: no open archive; the PMC /bin/ links answer a
     bot check, recorded, not worked around). A relayed value is never data: LIFE is not pooled until eTable 4 is held.
 (2) HARMS: the protocol prespecifies hypotension and hyperkalaemia; the topic config listed none, so the page said
     'none recorded'. Each row carries its own typed DEFINITION; different definitions are never pooled into one number
     (DEFINITION_MIX_POOLED, blocking):
       PARALLEL-HF (held, J-STAGE full text, Table 3; N 111 vs 112 -- two mis-randomised untreated patients excluded):
         hypotension = reported AE with SBP <90 mmHg 13 vs 5; serum potassium >=5.5 mmol/L (laboratory) 8 vs 6
       PARADIGM-HF (Table 3 relayed, NOT held -- NEJM 403, the Keele copy 403): symptomatic hypotension 588/4,187 vs
         388/4,212; potassium >5.5 mmol/L 674/4,187 vs 727/4,212; the held abstract reports both directions
       LIFE (held, registry results): symptomatic hypotension with SBP <=85 mmHg 29/167 vs 20/168; potassium >=5.5 mmol/L
         28/167 vs 15/168 (the paper and registry report ORs; our RRs would be reconstructed from counts, labelled so)
 (3) PARALLEL-HF: its publication (33731544) was excluded as 'not double-blind' from an abstract silent on masking, while
     the trial contributes through its registry. The held full text says double-blind: the publication is linked to the
     registry family (study_families) and the family invariant forbids a design exclusion in a contributing family.
 (4) PIONEER-HF (NCT02554890): main report 30415601, clinical-outcomes report 30955360, open-label extension 31825471 --
     one family. The exact 8-week clinical HR is NOT held (NEJM 403; the Circulation report is not open and its record
     has no abstract); the extension's 12-week HR 0.69 (0.49-0.97) spans the open-label switch and is declared NOT the
     8-week contrast (WRONG_WINDOW, blocking).
  PYTHONPATH=. python outputs/handover/sacubitril_sources/make_sacubitril_fixtures.py"""
import hashlib, json, os, re

SLUG = "sacubitril-valsartan-hfref"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
PRIM = "Composite cardiovascular death or heart-failure hospitalization"
HYPO, HYPK = "Hypotension", "Hyperkalemia"
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
    assert len(m) == 1, f"{where}: {len(m)} matches"
    return m[0]


def rec(t, pmid):
    p = f"{H}/{t}/europepmc_record_{pmid}.json"
    r = json.load(open(p, encoding="utf-8"))["resultList"]["result"][0]
    assert r["pmid"] == pmid, (p, r.get("pmid"))
    return p, r


# ------------------------------------------------------------------ PARALLEL-HF full text (CC BY-NC-ND, local; excerpt)
P_PDF, P_TXT = f"{H}/PARALLEL-HF/unpaywall.pdf", f"{H}/PARALLEL-HF/unpaywall.local.txt"
PT = open(P_TXT, encoding="utf-8").read()
P_DESIGN = once(PT, "Briefly, the study was a multicenter, randomized, double-blind study", "PARALLEL design")
P_MISRAND = local_once(PT, r"Two patients who did not meet eligibility criteria but were randomized by mistake did not "
                           r"receive double- ?blind treatment and were not included in the analyses for efficacy and "
                           r"safety outcomes \(one from each treatment group\)\.", "PARALLEL mis-randomised")
once(PT, "Table 3. Adverse Events During Double-Blind Treatment Period Adverse event Sacubitril/valsartan (N=111), n (%) "
         "Enalapril (N=112), n (%) P value", "PARALLEL Table 3 header")
once(PT, "Hypotension* with SBP <90 mmHg 13 (11.7) 5 (4.5) 0.0526", "PARALLEL hypotension row")
once(PT, "Elevated serum potassium (mmol/L) ≥5.5 8 (7.2) 6 (5.4) 0.5944", "PARALLEL potassium row")
once(PT, "*Based on reported term.", "PARALLEL footnote")
P_CODED = local_once(PT, r"the incidence of hyperkalemia was higher in the enalapril group compared with the "
                         r"sacubitril/valsartan group \(15\.2% vs\. 11\.7%; Supplementary Table 3\)", "PARALLEL coded hyperkalemia")
P_TAB = f"{X}/PARALLEL-HF_Table3_safety.tables.txt"
P_HYPO = "Hypotension* with SBP <90 mmHg | 13 (11.7) | 5 (4.5) | 0.0526"
P_HYPK = "Elevated serum potassium (mmol/L) ≥5.5 | 8 (7.2) | 6 (5.4) | 0.5944"
open(P_TAB, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of PARALLEL-HF Table 3 'Adverse Events During Double-Blind Treatment Period' (Tsutsui et al., Circ J 2021; "
    "J-STAGE publisher PDF, licence CC BY-NC-ND 4.0, held locally). Every value is verbatim from our pypdf text of the held "
    "PDF; the CELL BOUNDARIES are this excerpt's segmentation of that text run.\n"
    f"# held PDF: {P_PDF} sha256 {sha(P_PDF)}\n"
    f"# design (verbatim): {P_DESIGN}\n"
    f"# population (verbatim): {P_MISRAND}\n"
    "# footnote * (verbatim): *Based on reported term.\n"
    f"# NOT the laboratory row (verbatim, coded AE, a different definition): {P_CODED}\n\n"
    "=== TABLES (excerpt) ===\nTABLE Table 3. Adverse Events During Double-Blind Treatment Period\n"
    "Adverse event | Sacubitril/valsartan (N=111), n (%) | Enalapril (N=112), n (%) | P value\n"
    + P_HYPO + "\n" + P_HYPK + "\n")

# ------------------------------------------------------------------ LIFE: held main text (PMC page, local) + registry
L_HTML = f"{H}/LIFE/pmc_article.html"
_raw = open(L_HTML, encoding="utf-8", errors="replace").read()
import html as _h
LT = flat(_h.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", _raw))))
L_TERT = local_once(LT, r"There were no informative differences between the sacubitril/valsartan and valsartan treatment "
                        r"arms with respect to the tertiary end points that were examined, including death from "
                        r"cardiovascular causes or hospitalization for heart failure.{0,400}?\(eTable 4, eTable 5, and "
                        r"eFigure 4 in Supplement 2 ?\)\.", "LIFE tertiary sentence")
L_EX = f"{X}/LIFE_main_text_tertiary_endpoints.txt"
open(L_EX, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (one verbatim sentence) of a held document that is not redistributed: the PMC article page of LIFE "
    "(Mann et al., JAMA Cardiol 2022, PMC8567189; NIH manuscript), held locally\n"
    f"# held page: {L_HTML} sha256 {sha(L_HTML)}\n\n" + L_TERT + "\n")
LREC, lr = rec("LIFE", "34730769")
L_DESIGN = "A double-blind randomized clinical trial was conducted; a total of 335 patients with advanced heart failure were included."
assert L_DESIGN in lr["abstractText"], "LIFE design sentence"
LREG = f"{H}/LIFE-registration/NCT02816736.json"
lreg = json.load(open(LREG, encoding="utf-8"))
oms = {om["title"]: om for om in lreg["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"]}
L_POP = oms["Tolerability - Hypotension"]["populationDescription"]
assert "COVID-19" in L_POP
L_HYPO_DEF = oms["Tolerability - Hypotension"]["description"]
L_HYPK_DEF = oms["Tolerability - Hyperkalemia"]["description"]
L_ENROL = lreg["protocolSection"]["designModule"]["enrollmentInfo"]["count"]


def counts(om):
    cat = next(c for cl in om["classes"] for c in cl["categories"] if c.get("title") == "Yes")
    v = {m["groupId"]: int(m["value"]) for m in cat["measurements"]}
    n = {c["groupId"]: int(c["value"]) for c in om["denoms"][0]["counts"]}
    return v["OG000"], n["OG000"], v["OG001"], n["OG001"]


assert counts(oms["Tolerability - Hypotension"]) == (29, 167, 20, 168)
assert counts(oms["Tolerability - Hyperkalemia"]) == (28, 167, 15, 168)

# ------------------------------------------------------------------ PARADIGM-HF: the held abstract reports the direction
REC = f"cache/{SLUG}/records.json"
recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}
D_ABS = once(recs["25176015"]["abstract"], "The LCZ696 group had higher proportions of patients with hypotension and "
             "nonserious angioedema but lower proportions with renal impairment, hyperkalemia, and cough than the enalapril "
             "group.", "PARADIGM abstract")

# ------------------------------------------------------------------ hand entries
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])
va_p, ve_p = f"cache/{SLUG}/verified_arms.json", f"cache/{SLUG}/verified_effects.json"
va = json.load(open(va_p, encoding="utf-8")) if os.path.exists(va_p) else {}
ve = json.load(open(ve_p, encoding="utf-8"))


def put(store, pid, entry):
    rows = [r for r in as_list(store.get(pid)) if r.get("outcome") != entry["outcome"]] + [entry]
    store[pid] = rows if len(rows) > 1 else rows[0]


P_POP = "safety population of the double-blind period: 111 vs 112 (two mis-randomised patients who were never treated excluded)"
put(va, "NCT02468232", {
    "outcome": HYPO, "ai": 13, "n1i": 111, "ci": 5, "n2i": 112, "kind": "extracted_counts",
    "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
    "document_ref": P_TAB, "document_sha256": sha(P_TAB), "source_span": P_HYPO, "safety_population": P_POP,
    "harm_definition": "hypotension reported as an adverse event (reported term) WITH systolic blood pressure <90 mmHg",
    "harm_definition_key": "HYPOTENSION_AE_TERM_WITH_SBP_LT_90",
    "effect_reconstructed_from_counts": "the paper reports n (%) and a P value; the RR is reconstructed from the counts",
    "reason": ("PARALLEL-HF Table 3 (held full text; excerpt committed): hypotension (reported AE term) with SBP <90 mmHg, "
               "13/111 vs 5/112, double-blind period. Not the same definition as PARADIGM's symptomatic hypotension or "
               "LIFE's symptomatic SBP <=85.")})
put(va, "NCT02468232", {
    "outcome": HYPK, "ai": 8, "n1i": 111, "ci": 6, "n2i": 112, "kind": "extracted_counts",
    "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
    "document_ref": P_TAB, "document_sha256": sha(P_TAB), "source_span": P_HYPK, "safety_population": P_POP,
    "harm_definition": "serum potassium >=5.5 mmol/L (laboratory)",
    "harm_definition_key": "SERUM_K_GE_5_5_LAB",
    "effect_reconstructed_from_counts": "the paper reports n (%) and a P value; the RR is reconstructed from the counts",
    "reason": ("PARALLEL-HF Table 3: elevated serum potassium >=5.5 mmol/L (a LABORATORY definition), 8/111 vs 6/112. "
               "Not the paper's coded hyperkalemia adverse event (15.2% vs 11.7%, Supplementary Table 3), a different "
               "definition.")})
for outcome, rel in ((HYPO, "symptomatic hypotension 588/4,187 vs 388/4,212 (Table 3)"),
                     (HYPK, "potassium >5.5 mmol/L 674/4,187 vs 727/4,212 (Table 3, laboratory)")):
    put(ve, "25176015", {
        "outcome": outcome, "absent": True, "override": True, "provenance": "REFUSED_ON_EVIDENCE",
        "document_ref": f"{REC}#PMID-25176015", "source_span": D_ABS, "reported_unresolved_span": D_ABS,
        "reason": (f"PARADIGM-HF reports this harm: the held abstract gives its direction ('{D_ABS}'), without counts. "
                   f"The full report's {rel} is RELAYED, NOT HELD (NEJM 403; the Keele repository copy 403): shown beside "
                   "the row, never pooled, until the table is held.")})
dump(va_p, va)
dump(ve_p, ve)

rp = "docs/relayed_values.json"
rvd = json.load(open(rp, encoding="utf-8"))
rvd["values"] = [v for v in rvd["values"] if v["topic"] != SLUG]
for outcome, value, definition in (
        (HYPO, "588/4,187 LCZ696 vs 388/4,212 enalapril", "symptomatic hypotension (clinical; no blood-pressure threshold)"),
        (HYPK, "674/4,187 LCZ696 vs 727/4,212 enalapril", "serum potassium >5.5 mmol/L (laboratory)")):
    rvd["values"].append({
        "topic": SLUG, "trial": "PMID 25176015", "outcome": outcome, "value": f"{value}; definition: {definition}",
        "relayed_by": "the orchestrating lane (sacubitril-HFrEF review fixtures, 2026-09-28)",
        "said_to_be_in": "PARADIGM-HF, NEJM 2014, Table 3 (safety population 4,187 vs 4,212)",
        "why_not_held": ("NEJM PDF 403; the Keele repository copy 403; the Luxembourg repository unreachable; Europe PMC not "
                         "open access; the FDA ENTRESTO label gives rounded percentages of CODED adverse events (a different "
                         "definition). Recorded in evidence/acquisition_cascade/ATTEMPTS.jsonl (target PARADIGM-HF)."),
        "not_for": ["a pool with another definition of this harm"]})
dump(rp, rvd)

# ------------------------------------------------------------------ (3) PARALLEL-HF: one record, one design decision
sp = "docs/study_families.json"
sf = json.load(open(sp, encoding="utf-8"))
sf["topics"][SLUG] = [e for e in sf["topics"].get(SLUG) or [] if e.get("pmid") != "33731544"] + [{
    "pmid": "33731544", "parent": "PARALLEL-HF (NCT02468232, contributing through its registry record)",
    "parent_pmid": "NCT02468232",   # the parent RECORD id: this family is registry-anchored (no journal parent)
    "trial_family_id": "NCT02468232", "publication_role": "primary",
    "kind": ("primary publication of an already-pooled registry trial: one trial, one family, one design decision "
             "(double-blind, held full text), never a second trial and never a design exclusion"),
    "design_witness": W(P_TAB, P_DESIGN)}]
dump(sp, sf)

# ------------------------------------------------------------------ (4) PIONEER-HF: one family, three reports
m_p, m_r = rec("PIONEER-HF", "30415601")
o_p, o_r = rec("PIONEER-HF-outcomes", "30955360")
x_p, x_r = rec("PIONEER-HF-extension", "31825471")
M_SPAN = "Of the 881 patients who underwent randomization, 440 were assigned to receive sacubitril-valsartan and 441 to receive enalapril."
assert M_SPAN in m_r["abstractText"]
O_SPAN = o_r["title"]
assert "Clinical Outcomes in Patients With Acute Decompensated Heart Failure Randomly Assigned to Sacubitril/Valsartan or Enalapril" in O_SPAN
X_12WK = ("Over the entire 12 weeks of follow-up, patients that began taking sacubitril/valsartan in the hospital had a lower "
          "hazard for the composite outcome compared with patients that initiated enalapril in the hospital and then had a "
          "delayed initiation of sacubitril/valsartan 8 weeks later (hazard ratio, 0.69; 95% CI 0.49-0.97).")
assert X_12WK in x_r["abstractText"]
X_REC = "of 881 patients enrolled in PIONEER-HF, 832 (94%) continued in the open-label study"
assert X_REC in x_r["abstractText"]
rpp = "docs/registry_publications.json"
rpd = json.load(open(rpp, encoding="utf-8"))
rpd["topics"][SLUG] = [{
    "registration": "NCT02554890", "pmid": "30415601", "label": "PIONEER-HF main report (Velazquez, NEJM 2019)",
    "coverage": "ABSTRACT_ONLY (NEJM 403)", "record_witness": W(m_p, M_SPAN),
    "identity_check": "881 randomised (440 vs 441) in the report; one registration, NCT02554890",
    "reports": [
        {"pmid": "30955360", "label": "PIONEER-HF clinical outcomes (Morrow, Circulation 2019)", "role": "OUTCOMES_REPORT",
         "coverage": "RECORD_ONLY (no abstract in the record; not open access)", "record_witness": W(o_p, O_SPAN),
         "holds": "the 8-week clinical-outcome hazard ratios (not held)"},
        {"pmid": "31825471", "label": "PIONEER-HF open-label extension (DeVore, JAMA Cardiol 2020)", "role": "EXTENSION_REPORT",
         "coverage": "ABSTRACT_ONLY (PMC6990764 not open access; supplement not held)", "record_witness": W(x_p, X_REC),
         "holds": "week 8-12 open-label results and a 12-week composite HR spanning the switch"}],
    "per_outcome": {PRIM: {
        "statement": ("PIONEER-HF's 8-week clinical composite (CV death or HF rehospitalisation) is reported by the main "
                      "report and the clinical-outcomes report; neither is held (NEJM 403; the Circulation report is not "
                      "open and its record carries no abstract), and the registry posts no clinical outcome. The exact "
                      "8-week HR is not extracted: nothing is guessed."),
        "not_this": [{"why": ("the extension's 12-week HR spans weeks 8-12, when the enalapril arm switched to open-label "
                              "sacubitril/valsartan: a different window and a different contrast from the 8-week "
                              "randomised comparison"),
                      "witness": W(x_p, X_12WK)}]}}}]
dump(rpp, rpd)

# ------------------------------------------------------------------ (1) LIFE: known eligible, not in the inventory
kp = "docs/known_eligible_missing.json"
kd = json.load(open(kp, encoding="utf-8"))
kd["topics"][SLUG] = [e for e in kd["topics"].get(SLUG) or [] if e.get("trial") != "LIFE"] + [{
    "trial": "LIFE", "registration": "NCT02816736", "pmid": "34730769",
    "mechanism": ("inventory (absent from the committed search and registry inventory); eligible by protocol: double-blind, "
                  "sacubitril/valsartan vs valsartan -- an ARB active comparator (protocol C) -- in HFrEF"),
    "status": "source_held_result_in_supplement_not_held",
    "acquisition": {"route": ("acquisition cascade: Europe PMC record (abstract), the PMC article page (NIH manuscript, "
                              "held locally; excerpt committed), ClinicalTrials.gov posted results; supplement NOT held "
                              "(Europe PMC supplementaryFiles: no archive, not open access; PMC /bin/ links: bot check, "
                              "recorded, not worked around)"),
                    "held_path": L_EX, "held_sha256": sha(L_EX), "record_path": LREC, "record_sha256": sha(LREC),
                    "registration_path": LREG, "registration_sha256": sha(LREG)},
    "design": (f"double-blind (registry masking TRIPLE); randomised {L_ENROL}; principal analysis n=335 -- a COVID-related "
               "cohort restriction, NOT all randomised (registry: '" + L_POP + "'); 24 weeks"),
    "comparisons": "one family (NCT02816736): sacubitril/valsartan vs valsartan (+ matching placebos)",
    "design_note": (f"PRINCIPAL ANALYSIS n=335 of {L_ENROL} randomised: a COVID-related cohort restriction, NOT all "
                    "randomised. "
                    "NOT POOLED: its CV death or HF hospitalisation is reported in eTable 4 of Supplement 2, which is not "
                    "held; relayed (not data): 48/167 vs 37/168, HR 1.32 (0.86-2.03). Distinct outcomes in the same table, "
                    "never substituted: first HF hospitalisation HR 1.24 (0.80-1.93); total HF hospitalisations 61 vs 50 "
                    "EVENTS, rate ratio 1.23 (0.85-1.79) -- recurrent events, not patients. Diagnostic only (relayed): the "
                    "3-trial pool with LIFE would be 0.9724 (0.5024-1.8820) vs the served k=2 estimate. HARMS held (registry "
                    f"results, n 167 vs 168): '{L_HYPO_DEF}' 29 vs 20 (registry OR 1.55); '{L_HYPK_DEF}' 28 vs 15 (OR 2.05)."),
    "result_states": {PRIM: {
        "state": "REPORTED_UNRESOLVED", "span": L_TERT, "witness": W(L_EX, L_TERT),
        "basis": ("the held main text names the outcome and where it is (eTable 4, Supplement 2); the supplement is not held, "
                  "so the counts and HR are relayed, not held"),
        "relayed_not_held": {"value": "48/167 vs 37/168; HR 1.32 (0.86-2.03)", "said_to_be_in": "eTable 4, Supplement 2"}}},
    "harm_rows_held": {
        HYPO: {"definition": L_HYPO_DEF, "definition_key": "SYMPTOMATIC_HYPOTENSION_SBP_LE_85", "ai": 29, "n1i": 167,
               "ci": 20, "n2i": 168, "source_or": "OR 1.55 (0.84-2.87), logistic regression",
               "witness": W(LREG, L_HYPO_DEF)},
        HYPK: {"definition": L_HYPK_DEF, "definition_key": "SERUM_K_GE_5_5_LAB", "ai": 28, "n1i": 167, "ci": 15, "n2i": 168,
               "source_or": "OR 2.05 (1.05-4.00), logistic regression", "witness": W(LREG, L_HYPK_DEF)}}}]
dump(kp, kd)

# ------------------------------------------------------------------ outcome definitions (never pooled across)
# PIONEER-HF's harms reach the pool from its registry results; their definitions are the registry's own words
PREG = f"{H}/NCT02554890/NCT02554890.json"
p_oms = {om["title"]: om for om in json.load(open(PREG, encoding="utf-8"))["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"]}
PI_HYPO = p_oms["Number of Patients With Incidences of Symptomatic Hypotension"]["description"]
PI_HYPO = PI_HYPO[:PI_HYPO.index("during 8 weeks of treatment") + len("during 8 weeks of treatment")]
PI_HYPK = p_oms["Number of Patients With Incidences of Hyperkalemia"]["description"]
PI_HYPK = PI_HYPK[:PI_HYPK.index("mEq/L.") + len("mEq/L.")]
assert "symptomatic hypotension" in PI_HYPO and "5.5 mEq/L" in PI_HYPK
op = "docs/outcome_restrictions.json"
orx = json.load(open(op, encoding="utf-8"))
orx["topics"][SLUG] = {
    HYPO: {"restriction": "DEFINITION_TYPED",
           "definition": "each row carries its own definition: symptomatic (clinical), reported-AE-with-SBP-threshold, symptomatic-with-SBP-threshold",
           "definitions_seen": {"PARADIGM-HF": "symptomatic hypotension (relayed)", "PARALLEL-HF": "HYPOTENSION_AE_TERM_WITH_SBP_LT_90",
                                "LIFE": "SYMPTOMATIC_HYPOTENSION_SBP_LE_85 (known eligible, not pooled)"},
           "definitions_by_trial": {"NCT02554890": {"key": "SYMPTOMATIC_HYPOTENSION", "definition": PI_HYPO,
                                                    "witness": W(PREG, PI_HYPO)}}},
    HYPK: {"restriction": "DEFINITION_TYPED",
           "definition": "laboratory potassium thresholds (>5.5 vs >=5.5 mmol/L) are kept apart from CODED hyperkalaemia adverse events",
           "definitions_by_trial": {"NCT02554890": {"key": "SERUM_K_GT_5_5_LAB", "definition": PI_HYPK,
                                                    "witness": W(PREG, PI_HYPK)}},
           "definitions_seen": {"PARADIGM-HF": "potassium >5.5 mmol/L (relayed)", "PARALLEL-HF": "SERUM_K_GE_5_5_LAB",
                                "LIFE": "SERUM_K_GE_5_5_LAB (known eligible, not pooled)"}}}
dump(op, orx)
print("sacubitril fixtures written")
