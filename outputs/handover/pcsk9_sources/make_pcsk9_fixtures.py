"""PCSK9 review fixtures (2026-09-28). Every span is asserted against held bytes before it is written.
 (1) GLAGOV MACE: 'outcome_not_reported' was said of the ABSTRACT. The full report's Table 4 is said to give first MACE
     59/484 vs 74/484 (exploratory, adjudicated, safety population) -- relayed, NOT held (JAMA not open; the Amsterdam UMC
     PDF 403; the Jagiellonian repository copies unreachable, URLError, recorded; the registry posts no MACE). The row
     becomes NOT_YET_RETRIEVED (the report that holds the result is not held) with the relayed counts shown beside it;
     never 'not reported'. Component rows are never summed into a patient composite (harness/outcome_restriction.py).
 (2) ODYSSEY LONG TERM MACE: the post-hoc refusal STANDS. Its HR 0.52 (0.31-0.90) is held in a sentence that itself
     says 'In a post hoc analysis': EXTRACTED_NOT_ADMITTED, and the reason audit no longer calls the refusal false.
 (3) Safety rows from the trials' own Table 3s (held locally, committed as TABLES excerpts), safety populations:
     FOURIER injection-site 296/13,769 vs 219/13,756; ODYSSEY OUTCOMES injection-site 360/9,451 vs 203/9,443 and adverse
     event leading to discontinuation 343/9,451 vs 324/9,443. FOURIER's 'Thought to be related to the study agent and
     leading to discontinuation' 226 vs 201 is the ATTRIBUTION-restricted outcome, refused for the unrestricted one;
     ODYSSEY's 26 vs 3 injection-site discontinuations are a single CAUSE, never overall discontinuation.
  PYTHONPATH=. python outputs/handover/pcsk9_sources/make_pcsk9_fixtures.py"""
import hashlib, json, os, re


def dump(path, data):
    # keep the file's own indentation, so a rewrite diffs only what changed
    ind = 1
    if os.path.exists(path):
        raw = open(path, encoding="utf-8").read()
        m = re.match(r"\{\n( +)\"", raw)
        ind = len(m.group(1)) if m else 1
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(data, indent=ind, ensure_ascii=False) + "\n")


SLUG = "pcsk9-mace"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
MACE, ISR, DISC = "Major adverse cardiovascular events", "Injection-site reactions", "Adverse events leading to discontinuation"
F_TXT, F_PDF = f"{H}/PMID28304224/repository.local.txt", f"{H}/PMID28304224/repository.pdf"
O_TXT, O_PDF = f"{H}/PMID30403574/unpaywall.local.txt", f"{H}/PMID30403574/unpaywall.pdf"
F, O = flat(open(F_TXT, encoding="utf-8").read()), flat(open(O_TXT, encoding="utf-8").read())


def once(text, span, where):
    n = text.count(span)
    assert n == 1, f"{where}: {n} occurrences of {span!r}"
    return span


# ---------------------------------------------------------------- FOURIER Table 3 (safety population)
once(F, "Table 3. Adverse Events and Laboratory Test Results.", "FOURIER caption")
once(F, "Evolocumab (N = 13,769) Placebo (N = 13,756) Adverse events — no. of patients (%)", "FOURIER header")
once(F, "Thought to be related to the study agent and leading to discontinuation of study regimen 226 (1.6) 201 (1.5)", "FOURIER attributed")
once(F, "Injection-site reaction* 296 (2.1) 219 (1.6)", "FOURIER injection-site")
F_POP = once(F, "Safety evalu- ations included all the patients who underwent randomization and received at least one dose of "
                "a study agent and for whom post-dose data were available.", "FOURIER population")
F_TAB = f"{X}/FOURIER_Table3_safety.tables.txt"
F_ATT = "Thought to be related to the study agent and leading to discontinuation of study regimen | 226 (1.6) | 201 (1.5)"
F_ISR = "Injection-site reaction* | 296 (2.1) | 219 (1.6)"
open(F_TAB, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of FOURIER Table 3 'Adverse Events and Laboratory Test Results' (Sabatine et al., NEJM 2017; published "
    "version in the Archive ouverte UNIGE, unige:111533, held locally, not redistributed). Every value is verbatim from our "
    "pypdf text of the held PDF; the CELL BOUNDARIES are this excerpt's segmentation of that text run.\n"
    f"# held PDF: {F_PDF} sha256 {sha(F_PDF)}\n"
    f"# population (verbatim, methods): {F_POP}\n"
    "# footnote * (verbatim): The between-group difference was nominally significant (P<0.001).\n\n"
    "=== TABLES (excerpt) ===\nTABLE Table 3. Adverse Events and Laboratory Test Results.\n"
    "Outcome | Evolocumab (N = 13,769) | Placebo (N = 13,756)\nAdverse events — no. of patients (%)\n"
    + F_ATT + "\n" + F_ISR + "\n")

# ---------------------------------------------------------------- ODYSSEY OUTCOMES Table 3 (safety population)
once(O, "Table 3. Adverse Events and Laboratory Abnormalities.", "ODYSSEY caption")
once(O, "Variable Alirocumab (N = 9451) Placebo (N = 9443) Adverse events — no. (%)", "ODYSSEY header")
once(O, "Adverse event that led to discontinuation of the trial regimen 343 (3.6) 324 (3.4)", "ODYSSEY discontinuation")
once(O, "Local injection-site reaction 360 (3.8) 203 (2.1)", "ODYSSEY injection-site")
O_26 = once(O, "Injection-site reactions (itching, redness, or swelling) were usually mild and self- limited and led to "
               "discontinuation of the trial regimen in 26 patients in the alirocumab group, at a median of 8.3 months after "
               "randomization, and in 3 patients in the placebo group.", "ODYSSEY 26 vs 3")
O_TAB = f"{X}/ODYSSEY-OUTCOMES_Table3_safety.tables.txt"
O_DISC = "Adverse event that led to discontinuation of the trial regimen | 343 (3.6) | 324 (3.4)"
O_ISR = "Local injection-site reaction | 360 (3.8) | 203 (2.1)"
open(O_TAB, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT of ODYSSEY OUTCOMES Table 3 'Adverse Events and Laboratory Abnormalities' (Schwartz et al., NEJM 2018; "
    "accepted manuscript, publicatio.bibl.u-szeged.hu/27059, licence other-oa, held locally, not redistributed). Every "
    "value is verbatim from our pypdf text of the held PDF; the CELL BOUNDARIES are this excerpt's segmentation.\n"
    f"# held PDF: {O_PDF} sha256 {sha(O_PDF)}\n"
    "# population: the table's own denominators, alirocumab N = 9451, placebo N = 9443 (9462 randomised per arm): the "
    "safety population\n"
    f"# NOT overall discontinuation (verbatim, results): {O_26}\n\n"
    "=== TABLES (excerpt) ===\nTABLE Table 3. Adverse Events and Laboratory Abnormalities.\n"
    "Variable | Alirocumab (N = 9451) | Placebo (N = 9443)\nAdverse events — no. (%)\n"
    + O_DISC + "\n" + O_ISR + "\n")

# ---------------------------------------------------------------- hand entries
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])
va_p, ve_p = f"cache/{SLUG}/verified_arms.json", f"cache/{SLUG}/verified_effects.json"
va, ve = json.load(open(va_p, encoding="utf-8")), json.load(open(ve_p, encoding="utf-8"))


def take(store, pid, outcome):
    """remove and return the entry for (pid, outcome) from a store (None if absent)"""
    rows = as_list(store.get(pid))
    old = next((r for r in rows if r.get("outcome") == outcome), None)
    rest = [r for r in rows if r.get("outcome") != outcome]
    if rest:
        store[pid] = rest if len(rest) > 1 else rest[0]
    else:
        store.pop(pid, None)
    return old


def put(store, pid, entry):
    # replaced IN PLACE (a key keeps its position, so a rerun writes identical bytes)
    rows = [r for r in as_list(store.get(pid)) if r.get("outcome") != entry["outcome"]] + [entry]
    store[pid] = rows if len(rows) > 1 else rows[0]


def superseded(pid, outcome, new_prov):
    """the earlier decision this entry replaces: from verified_effects, or kept from a previous run of this script"""
    old = take(ve, pid, outcome)
    prev = next((r for r in as_list(va.get(pid)) if r.get("outcome") == outcome and r.get("provenance") == new_prov), None)
    if old and not (old.get("document_ref") or "").startswith(X):
        return {k: old.get(k) for k in ("provenance", "reason") if old.get(k)}
    return (prev or {}).get("supersedes")


def arms(pid, outcome, ai, n1, ci, n2, tab, row, pop, why):
    sup = superseded(pid, outcome, "fulltext_verified_arms")
    put(va, pid, {"outcome": outcome, "ai": ai, "n1i": n1, "ci": ci, "n2i": n2, "kind": "extracted_counts",
                  "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
                  "document_ref": tab, "document_sha256": sha(tab), "source_span": row, "safety_population": pop,
                  "attribution": "ANY", **({"supersedes": sup} if sup else {}), "reason": why})


F_POPTXT = "safety population: randomised patients who received at least one dose with post-dose data (13,769 evolocumab vs 13,756 placebo)"
O_POPTXT = "safety population: the table's denominators, 9451 alirocumab vs 9443 placebo (9462 randomised per arm)"
arms("28304224", ISR, 296, 13769, 219, 13756, F_TAB, F_ISR, F_POPTXT,
     "FOURIER injection-site reaction from Table 3 of the trial's own report (published version, held locally; committed as a "
     "TABLES excerpt): 296/13,769 vs 219/13,756, safety population.")
arms("30403574", ISR, 360, 9451, 203, 9443, O_TAB, O_ISR, O_POPTXT,
     "ODYSSEY OUTCOMES local injection-site reaction from Table 3 of the accepted manuscript (held locally; committed as a "
     "TABLES excerpt): 360/9,451 vs 203/9,443, safety population.")
arms("30403574", DISC, 343, 9451, 324, 9443, O_TAB, O_DISC, O_POPTXT,
     "ODYSSEY OUTCOMES adverse event that led to discontinuation of the trial regimen (unrestricted: any adverse event), "
     "Table 3: 343/9,451 vs 324/9,443, safety population. NOT the 26 vs 3 injection-site discontinuations (one cause).")

# FOURIER: only the ATTRIBUTION-restricted row is held -- refused for the unrestricted outcome, shown as held
old = take(ve, "28304224", DISC)
sup = ({k: old.get(k) for k in ("provenance", "reason") if old.get(k)} if old and not str(old.get("document_ref") or "").startswith(X)
       else (old or {}).get("supersedes"))
put(ve, "28304224", {
    "outcome": DISC, "absent": True, "override": True, "provenance": "REFUSED_ON_EVIDENCE",
    "document_ref": F_TAB, "document_sha256": sha(F_TAB), "source_span": F_ATT, "source_level": 1,
    "held_out_row": {"ai": 226, "n1i": 13769, "ci": 201, "n2i": 13756},
    "attribution": "TREATMENT_ATTRIBUTED",
    "not_admitted_because": ("the held row is ATTRIBUTION-restricted ('Thought to be related to the study agent and leading "
                             "to discontinuation', 226 vs 201): a different outcome from any adverse event leading to "
                             "discontinuation, which the held Table 3 does not give"),
    **({"supersedes": sup} if sup else {}),
    "reason": ("FOURIER Table 3 gives discontinuation only for adverse events thought to be related to the study agent "
               "(226/13,769 vs 201/13,756): the investigator's attribution field restricts it. This review's outcome is any "
               "adverse event leading to discontinuation; the restricted row is held and shown, never pooled here.")})

# ODYSSEY LONG TERM MACE: the post-hoc refusal stands; its HR is held in a sentence that says post hoc
REC = f"cache/{SLUG}/records.json"
recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}
LT = once(recs["25773378"]["abstract"], "In a post hoc analysis, the rate of major adverse cardiovascular events (death from "
          "coronary heart disease, nonfatal myocardial infarction, fatal or nonfatal ischemic stroke, or unstable angina "
          "requiring hospitalization) was lower with alirocumab than with placebo (1.7% vs. 3.3%; hazard ratio, 0.52; 95% "
          "confidence interval, 0.31 to 0.90; nominal P=0.02).", "ODYSSEY LONG TERM abstract")
lt = next(r for r in as_list(ve["25773378"]) if r.get("outcome") == MACE)
lt.update({"source_span": LT, "document_ref": f"{REC}#PMID-25773378",
           "held_out_row": {"effect": 0.52, "ci_low": 0.31, "ci_high": 0.90, "scale": "HR"},
           "not_admitted_because": ("the analysis is post hoc (the held sentence says so): the refusal is about the "
                                    "analysis, not the value's presence, so the held HR 0.52 (0.31-0.90) does not lift it")})

# GLAGOV MACE: never 'not reported'; the report that holds it is not held
gl = next(r for r in as_list(ve["27846344"]) if r.get("outcome") == MACE)
gl.pop("absent_kind", None)
gl.update({"state": "OUTCOME_NOT_IN_SOURCE",
           "reason": ("the inspected ABSTRACT does not report MACE (its primary measure is percent atheroma volume by IVUS). "
                      "That is a statement about the abstract: the full report's Table 4 is said to report first MACE; it is "
                      "not held (see the acquisition state), so this is not a statement that the trial did not report it.")})
for p, d in ((va_p, va), (ve_p, ve)):
    dump(p, d)

# ---------------------------------------------------------------- declarations
ap = "docs/acquisition_states.json"
acq = json.load(open(ap, encoding="utf-8"))
acq["topics"][SLUG] = {"27846344": [{
    "outcome": MACE, "states": ["MAIN_RESULT_NOT_HELD"],
    "basis": ("GLAGOV's clinical-event table (Table 4 of the JAMA 2016 report: first MACE, exploratory, adjudicated, safety "
              "population) is not held: publisher copy not open; Amsterdam UMC repository PDF 403; the Jagiellonian "
              "University repository copies answered a network error twice (recorded, not worked around); the "
              "ClinicalTrials.gov results post no MACE measure. Counts relayed, not held: 59/484 vs 74/484. A compatible "
              "HR is unresolved."),
    "attempts": ["unpaywall_location 200 (pure.amsterdamumc.nl landing) -> repository_pdf BLOCKED_HTTP_403",
                 "repository_landing ERROR URLError (ruj.uj.edu.pl, twice)", "europepmc_fulltext NOT_OPEN_ACCESS",
                 "registry_results 200 (no MACE outcome measure)"]}]}
dump(ap, acq)

rp = "docs/relayed_values.json"
rv = json.load(open(rp, encoding="utf-8"))
rv["values"] = [v for v in rv["values"] if not (v["topic"] == SLUG and v["trial"] == "PMID 27846344")]
rv["values"].append({
    "topic": SLUG, "trial": "PMID 27846344", "outcome": MACE,
    "value": "first MACE 59/484 evolocumab vs 74/484 placebo (Table 4; exploratory, adjudicated; safety population)",
    "relayed_by": "the orchestrating lane (PCSK9 review fixtures, 2026-09-28)",
    "said_to_be_in": "GLAGOV, JAMA 2016, Table 4",
    "why_not_held": ("JAMA full text not open; the Amsterdam UMC repository PDF 403; the Jagiellonian repository unreachable "
                     "(URLError, twice); the registry posts no MACE; recorded in evidence/acquisition_cascade/ATTEMPTS.jsonl"),
    "not_for": ["a patient composite built by summing Table 4's component rows (a patient with two components would count twice)"]})
dump(rp, rv)

op = "docs/outcome_restrictions.json"
orx = json.load(open(op, encoding="utf-8")) if os.path.exists(op) else {
    "_doc": ("Outcome restrictions (harness/outcome_restriction.py): an UNRESTRICTED outcome never pools a row restricted by "
             "attribution or cause; the markers are verbatim phrasings of the restriction."), "topics": {}}
orx["topics"][SLUG] = {DISC: {
    "restriction": "UNRESTRICTED",
    "definition": "any adverse event leading to discontinuation of the trial regimen, whatever its attribution or cause",
    "refuse_markers": [r"related to the study (?:agent|drug)", r"thought to be related", r"treatment[- ]related",
                       r"because of an? injection[- ]site", r"injection[- ]site reactions?\b[^.]{0,160}led to discontinuation"],
    "examples_refused": {"FOURIER": F_ATT, "ODYSSEY OUTCOMES": O_26}}}
dump(op, orx)
print("PCSK9 fixtures written: 2 excerpts, 3 arm entries, FOURIER restricted refusal, ODYSSEY LT post-hoc, GLAGOV state, declarations")
