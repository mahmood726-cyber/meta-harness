"""Semaglutide-obesity (SELECT, MACE review) fixtures, 2026-09-28. Every span is asserted against held bytes first.
 (1) NOT_SYSTEMATICALLY_COLLECTED: SELECT collected safety selectively -- 'the only adverse events systematically
     recorded and reported were serious adverse events, adverse events leading to discontinuation of the trial product
     irrespective of seriousness, and adverse events of prespecified special interest' (Table 4 footnote); 'Nonserious
     AEs not fulfilling any of the listed criteria were not systematically collected' (Kushner et al., Obesity 2025).
     'Any GI adverse event' was never ascertained: NOT_SYSTEMATICALLY_COLLECTED, never zero, never manufactured by
     summing the serious-GI and GI-discontinuation rows (a patient can be in both).
 (2) SELECT Table 4 (patients; the investigator-reported safety table, N 8803 vs 8801), each its OWN outcome:
     serious adverse events 2941 vs 3204; serious GI adverse events 342 vs 323 (nested under serious AEs);
     GI adverse events leading to permanent discontinuation 880 vs 172 (nested under discontinuation).
     'Gastrointestinal disorders' appears TWICE in Table 4 under different parents: each is excerpted in its own table.
 (3) REPORT FAMILY: Kushner 2025 (PMID 39948761) is SELECT's dedicated safety report; the HbA1c analysis (PMID
     38907684) is a prespecified secondary analysis of SELECT whose held abstract states the SAME population -- both
     linked to SELECT (never a new trial; subgroup HRs never pooled). The MACE result is unchanged by the newer paper.
 (4) SELECT's family: the entry population is ESTABLISHED from source witnesses (registry criteria + the primary
     report's enrolment sentence), not from the registry's condition labels ('Overweight; Obesity').
  PYTHONPATH=. python outputs/handover/semaglutide_sources/make_semaglutide_mace_fixtures.py"""
import hashlib, html, json, os, re

SLUG = "semaglutide-obesity-mace"
H = "evidence/acquisition_cascade/held"
X = "evidence/acquisition_cascade/excerpts"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
flat = lambda s: re.sub(r"\s+", " ", s).strip()
W = lambda p, s: {"path": p, "sha256": sha(p), "span": s}
GI, SAE, SGI, GIDISC = ("Gastrointestinal adverse events", "Serious adverse events",
                        "Serious gastrointestinal adverse events", "Gastrointestinal adverse events leading to permanent discontinuation")


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


# ------------------------------------------------------------------ SELECT Table 4 (UCL copy of the NEJM PDF; local)
S_PDF, S_TXT = f"{H}/SELECT/unpaywall.pdf", f"{H}/SELECT/repository.local.txt"
ST = open(S_TXT, encoding="utf-8").read()
HEAD = once(ST, "Table 4. Investigator-Reported Adverse Events.* Event Semaglutide (N = 8803) Placebo (N = 8801) P Value† "
                "no. of patients (%)", "Table 4 header")
once(ST, "Serious adverse events‡ 2941 (33.4) 3204 (36.4) <0.001", "SAE row")
once(ST, "Gastrointestinal disorders 342 (3.9) 323 (3.7) 0.48", "serious GI row")
once(ST, "Adverse events leading to permanent discontinuation of trial product, irrespective of seriousness‡ 1461 (16.6) "
         "718 (8.2) <0.001 Gastrointestinal disorders 880 (10.0) 172 (2.0) <0.001", "discontinuation rows")
RULE = local_once(ST, r"the only adverse events systematically recorded and reported were serious adverse events, adverse "
                      r"events leading to discontinuation of the trial product irrespective of seriousness, and adverse "
                      r"events of prespecified special interest irrespective of seriousness\.", "collection rule")
SX = f"{X}/SELECT_Table4_serious.tables.txt"
DX = f"{X}/SELECT_Table4_discontinuation.tables.txt"
R_SAE = "Serious adverse events‡ | 2941 (33.4) | 3204 (36.4) | <0.001"
R_SGI = "Gastrointestinal disorders | 342 (3.9) | 323 (3.7) | 0.48"
R_DSC = "Adverse events leading to permanent discontinuation of trial product, irrespective of seriousness‡ | 1461 (16.6) | 718 (8.2) | <0.001"
R_GID = "Gastrointestinal disorders | 880 (10.0) | 172 (2.0) | <0.001"
HDR = ("# EXCERPT of SELECT Table 4 'Investigator-Reported Adverse Events' (Lincoff et al., NEJM 2023; repository copy "
       "discovery.ucl.ac.uk/10184940, held locally, not redistributed). Every value is verbatim from our pypdf text of the held "
       "PDF; the CELL BOUNDARIES are this excerpt's segmentation.\n"
       f"# held PDF: {S_PDF} sha256 {sha(S_PDF)}\n# collection rule (verbatim, Table 4 footnote): {RULE}\n")
open(SX, "w", encoding="utf-8", newline="\n").write(
    HDR + "# section: serious adverse events (GI disorders = SERIOUS GI adverse events)\n\n=== TABLES (excerpt) ===\n"
    "TABLE Table 4. Investigator-Reported Adverse Events. Serious adverse events\n"
    "Event | Semaglutide (N = 8803) no. of patients (%) | Placebo (N = 8801) no. of patients (%) | P Value\n"
    + R_SAE + "\n" + "Serious adverse events: " + R_SGI + "\n")
open(DX, "w", encoding="utf-8", newline="\n").write(
    HDR + "# section: adverse events leading to permanent discontinuation (GI disorders = GI adverse events LEADING TO "
    "DISCONTINUATION)\n\n=== TABLES (excerpt) ===\n"
    "TABLE Table 4. Investigator-Reported Adverse Events. Adverse events leading to permanent discontinuation\n"
    "Event | Semaglutide (N = 8803) no. of patients (%) | Placebo (N = 8801) no. of patients (%) | P Value\n"
    + R_DSC + "\n" + "Gastrointestinal adverse events leading to permanent discontinuation: " + R_GID + "\n")

# Kushner 2025 (CC BY-NC 4.0, Europe PMC XML held locally): the collection rule, excerpted
K_XML = f"{H}/SELECT-safety-Kushner2025/PMC11897845.xml"
KT = flat(html.unescape(re.sub(r"<[^>]+>", " ", open(K_XML, encoding="utf-8").read())))
K_RULE = once(KT, "Nonserious AEs not fulfilling any of the listed criteria were not systematically collected.", "Kushner rule")
K_AREAS = once(KT, "Targeted collection of safety data focused on the following three areas: all investigator‐reported serious "
                   "AEs (SAEs); AEs leading to treatment discontinuation irrespective of seriousness; and prespecified AEs of "
                   "special interest irrespective of seriousness.", "Kushner areas")
KX = f"{X}/SELECT_Kushner2025_collection_rule.txt"
open(KX, "w", encoding="utf-8", newline="\n").write(
    "# EXCERPT (verbatim sentences) of Kushner et al., 'Safety profile of semaglutide versus placebo in the SELECT study', "
    "Obesity 2025 (PMID 39948761, PMC11897845; CC BY-NC 4.0, held locally as Europe PMC XML)\n"
    f"# held XML: {K_XML} sha256 {sha(K_XML)}\n\n{K_AREAS}\n{K_RULE}\n")

# ------------------------------------------------------------------ hand entries: each safety row its own outcome
va_p = f"cache/{SLUG}/verified_arms.json"
va = json.load(open(va_p, encoding="utf-8"))
as_list = lambda v: v if isinstance(v, list) else ([v] if v else [])


def put(store, pid, entry):
    rows = [r for r in as_list(store.get(pid)) if r.get("outcome") != entry["outcome"]] + [entry]
    store[pid] = rows if len(rows) > 1 else rows[0]


POP = "investigator-reported safety table, all randomised patients (8803 vs 8801), in-trial"
for outcome, a, c, tab, span, why in (
        (SAE, 2941, 3204, SX, R_SAE, "any serious adverse event"),
        (SGI, 342, 323, SX, "Serious adverse events: " + R_SGI, "serious gastrointestinal adverse events (GI disorders among SERIOUS AEs)"),
        (GIDISC, 880, 172, DX, "Gastrointestinal adverse events leading to permanent discontinuation: " + R_GID,
         "gastrointestinal adverse events leading to permanent discontinuation (GI disorders among the discontinuation AEs)")):
    put(va, "37952131", {
        "outcome": outcome, "ai": a, "n1i": 8803, "ci": c, "n2i": 8801, "kind": "extracted_counts",
        "provenance": "fulltext_verified_arms", "source_level": 1, "override": True,
        "document_ref": tab, "document_sha256": sha(tab), "source_span": span, "safety_population": POP,
        "reason": (f"SELECT Table 4 (patients, not events): {why}, {a}/8803 vs {c}/8801. Its own outcome, never summed with "
                   "another Table 4 row into a GI total.")})
dump(va_p, va)

# ------------------------------------------------------------------ (1) collection scope
cp = "docs/collection_scope.json"
cs = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {
    "_doc": ("What a trial's safety collection did NOT ascertain (harness/collection_scope.py): NOT_SYSTEMATICALLY_COLLECTED, "
             "distinct from not reported / not retrieved / zero. Each declaration carries held witnesses of the collection rule."),
    "topics": {}}
cs["topics"][SLUG] = [{
    "trial": "PMID 37952131", "outcome": GI,
    "collected": ("serious adverse events; adverse events leading to permanent discontinuation irrespective of seriousness; "
                  "prespecified adverse events of special interest"),
    "not_collected": "non-serious adverse events that met none of those criteria -- so 'any GI adverse event' was never ascertained",
    "why": ("never a sum of the serious-GI (342 vs 323) and GI-discontinuation (880 vs 172) rows: a patient can be in both, and "
            "a non-serious GI event that did not lead to discontinuation was never recorded"),
    "collection_rule_witnesses": [W(SX, RULE), W(KX, K_RULE)]}]
dump(cp, cs)

# ------------------------------------------------------------------ (3) report family
sp = "docs/study_families.json"
sf = json.load(open(sp, encoding="utf-8"))
REC = f"cache/{SLUG}/records.json"
recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}
H_POP = once(recs["38907684"]["abstract"], "In SELECT, people with overweight or obesity and atherosclerotic cardiovascular "
             "disease without diabetes were randomized to weekly semaglutide 2.4 mg or placebo.", "HbA1c population")
sf["topics"][SLUG] = [e for e in sf["topics"].get(SLUG) or [] if e.get("pmid") not in ("38907684", "39948761")] + [
    {"pmid": "38907684", "parent": "SELECT (37952131, NCT03574597)", "parent_pmid": "37952131", "trial_family_id": "NCT03574597",
     "publication_role": "secondary_analysis",
     "kind": ("prespecified secondary analysis of SELECT by baseline HbA1c: never a new trial; its subgroup HRs are never "
              "pooled alongside the overall result. Its held abstract states the SAME population (the X2 'population not "
              "established' came from a title-keyword test, not from the source)"),
     "population_witness": W(REC, H_POP)},
    {"pmid": "39948761", "parent": "SELECT (37952131, NCT03574597)", "parent_pmid": "37952131", "trial_family_id": "NCT03574597",
     "publication_role": "safety_report",
     "kind": ("SELECT's dedicated safety report (Kushner et al., Obesity 2025): the source of the collection rules. "
              "Outcome-specific source selection: it never supersedes the primary report's MACE result")}]
dump(sp, sf)

# ------------------------------------------------------------------ (4) population witness for SELECT's family
REG = f"{H}/SELECT-registration/NCT03574597.json"
crit = json.load(open(REG, encoding="utf-8"))["protocolSection"]["eligibilityModule"]["eligibilityCriteria"]
C_CVD = re.search(r"Have established cardiovascular \(CV\) disease as evidenced by at least one of the following[^\n]*", crit).group(0)
C_DM = "History of type 1 or type 2 diabetes (history of gestational diabetes is allowed)"
assert C_DM in crit
S_ENROL = once(recs["37952131"]["abstract"], "we enrolled patients 45 years of age or older who had preexisting cardiovascular "
               "disease and a body-mass index (the weight in kilograms divided by the square of the height in meters) of 27 or "
               "greater but no history of diabetes", "SELECT enrolment")
pp = "docs/population_witnesses.json"
pw = json.load(open(pp, encoding="utf-8")) if os.path.exists(pp) else {
    "_doc": ("Entry-population decisions from SOURCE witnesses (harness/trial_family.population_witness): registry eligibility "
             "criteria and the primary report's enrolment sentence, each re-verified. States follow evid2's "
             "population_witness (EXCLUDED / CONFLICT / MIXED / ESTABLISHED / NOT_ESTABLISHED); only ESTABLISHED admits."),
    "topics": {}}
pw["topics"][SLUG] = {"NCT03574597": {
    "state": "ESTABLISHED",
    "basis": ("the protocol's population (overweight or obesity, established cardiovascular disease, no diabetes) is stated by an "
              "INCLUSION criterion (established CV disease; BMI >= 27), an EXCLUSION criterion (history of type 1 or type 2 "
              "diabetes) and the primary report's enrolment sentence; the registry condition labels ('Overweight; Obesity') "
              "are the registrant's topic, not an entry criterion"),
    "decided_by": "evidence lane (Claude Opus 5.5), 2026-09-28, source-backed",
    "witnesses": [{"kind": "registry inclusion criterion", "witness": W(REG, C_CVD)},
                  {"kind": "registry exclusion criterion", "witness": W(REG, C_DM)},
                  {"kind": "primary report enrolment sentence", "witness": W(REC, S_ENROL)}]}}
dump(pp, pw)
print("semaglutide-MACE fixtures written")
