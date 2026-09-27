"""Melatonin (primary insomnia, sleep-onset latency) fixtures, 2026-09-28. Every span asserted against held bytes first.
 (1) Wade 2011 (PMID 21091391) = further analysis of the SAME trial as Wade 2010 (NCT00397189): a companion report,
     one family. Its Table 3 (all adults 18-80 and 55-80, 3-week diary latency) is NOT openly held (Curr Med Res Opin:
     Europe PMC not OA, Unpaywall no open location): the values are recorded as RELAYED in a version chain whose governing
     decision is PENDING -- the protocol itself adopted the 65-80 pre-specified subgroup as the disclosed analysis
     population, so switching is a protocol decision, not a correction. (Wade 2010's own Table 3 has no all-adult row:
     its other block is the LOW-EXCRETOR subgroup, n 86 vs 86.)
 (2) Lemoine (PMID 22346363): a post-hoc pooled analysis of FOUR already-counted RCTs (refs 25-28: 18036082, 19584739,
     20712869, 17875243); its safety set also pools single-blind and open-label studies. Never new participants.
 (4) Wade 2010 ARM-LABEL CONFLICT: PDF Table 8 (394 placebo / 395 melatonin) vs PDF Table 9 and the held XML (394
     melatonin / 395 placebo); adjudicated only by corroboration independent of the article (the registry's posted results).
 (5) Luthringer 2009 (PMID 19584739): randomised treatment is 3 weeks (the rest is run-in / withdrawal); SOL reported
     as a between-group difference without SDs -> 'outcome reported; analysis-ready extraction pending'.
  PYTHONPATH=. python outputs/handover/melatonin_sources/make_melatonin_fixtures.py"""
import hashlib, json

from harness.report_family import _witness_text

SLUG = "melatonin-primary-insomnia-sol"
H = "evidence/acquisition_cascade/held/"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def W(path, span):
    w = {"path": path, "sha256": sha(path), "span": span}
    assert " ".join(span.split()) in " ".join(_witness_text(".", w).split()), (path, span[:90])
    return w


def RAW(path, start, end):
    raw = open(path, encoding="utf-8").read()
    i = raw.index(start)
    j = raw.index(end, i) + len(end)
    return {"path": path, "sha256": sha(path), "span": raw[i:j], "representation": "raw bytes"}


# ---------------------------------------------------------------- (1)+(2) companions (screening collapses them: X-DEDUP)
sfp = "docs/study_families.json"
sf = json.load(open(sfp, encoding="utf-8"))
sf["topics"][SLUG] = [
    {"pmid": "21091391", "parent": "Wade 2010 (20712869, NCT00397189)", "parent_pmid": "20712869",
     "trial_family_id": "NCT00397189",
     "kind": "further analysis of the same trial (companion report): one trial, one family, never a second trial"},
    {"pmid": "22346363", "parent": "four already-counted RCTs: 18036082, 19584739, 20712869, 17875243",
     "kind": ("post-hoc pooled analysis of four RCTs (its safety set also pools single-blind and open-label studies): "
              "linked to its constituent trials, never new participants")}]
open(sfp, "w", encoding="utf-8", newline="\n").write(json.dumps(sf, indent=1, ensure_ascii=False) + "\n")

LEM = f"cache/{SLUG}/ft_22346363.txt"
REC = f"cache/{SLUG}/records.json"
recs = {str(r["id"]): r for r in json.load(open(REC, encoding="utf-8"))["records"]}
lemoine = {
    "report_id": "PMID 22346363",
    "citation": "Lemoine P, Zisapel N et al. Integr Blood Press Control 2012;5:9-17 (post-hoc pooled analysis), DOI 10.2147/IBPC.S27240",
    "kind": "POOLED_ANALYSIS_OF_CONSTITUENT_TRIALS",
    "trials": [{"label": lab, "registration": reg, "reports": [f"PMID {pid}"],
                "population": {"witness": W(REC, recs[pid]["title"])}}
               for lab, reg, pid in (("Lemoine 2007", "PMID:18036082", "18036082"), ("Luthringer 2009", "PMID:19584739", "19584739"),
                                     ("Wade 2010", "NCT00397189", "20712869"), ("Wade 2007", "PMID:17875243", "17875243"))],
    "combined_analyses": [
        {"label": "Lemoine post-hoc efficacy pool (antihypertensive-treated subpopulations, 3 weeks)", "n": 392, "policy": "NEVER_IMPORTED",
         "witness": W(LEM, "Post hoc analysis of pooled antihypertensive drug-treated subpopulations from four randomized, double-blind trials of PRM and placebo for 3 weeks")},
        {"label": "Lemoine safety pool (the four RCTs plus three single-blind and open-label studies)", "n": 1282, "policy": "NEVER_IMPORTED",
         "witness": W(LEM, "three additional single-blind and open-label PRM studies of up to 1 year")}],
    "constituents_witness": W(LEM, "A post hoc, pooled analysis of four randomized, double-blind trials (short-term 3-week studies and a long-term 6-month study)"),
    "full_text_state": "HELD (committed PMC text, cache ft_22346363.txt)",
}
mp = "docs/multi_trial_reports.json"
m = json.load(open(mp, encoding="utf-8"))
m["reports"] = [r for r in m["reports"] if r["report_id"] != lemoine["report_id"]] + [lemoine]
open(mp, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- (1) the Wade SOL version chain, governing PENDING
FT2010 = f"cache/{SLUG}/ft_20712869.txt"
sp = "docs/source_versions.json"
sv = json.load(open(sp, encoding="utf-8"))
sv["topics"][SLUG] = [{
    "chain_id": "NCT00397189:SOL-diary-3wk", "trial_id": "PMID 20712869", "outcome": "Sleep-onset latency",
    "versions": [
        {"version_id": "v0-2010-subgroup-65-80", "kind": "ORIGINAL", "date": "2010",
         "source": "Wade 2010 (BMC Med, PMID 20712869) Table 3: the pre-specified 65-80 year population",
         "held": W(FT2010, "65-80 year population N 137 144 Baseline: mean (SD) 76.7 (63.7) 72.5 (51.4) Treatment: mean (SD) 57.6 (51.8) 70.9 (54.0) Change from baseline: mean (SD) -19.1 (47.3) -1.7 (47.8)"),
         "value": {"mean1": -19.1, "sd1": 47.3, "nc1": 137, "mean2": -1.7, "sd2": 47.8, "nc2": 144}},
        {"version_id": "v1-2011-all-adults-18-80", "kind": "COMPANION_REPORT", "date": "2011",
         "source": "Wade 2011 (Curr Med Res Opin, PMID 21091391, DOI 10.1185/03007995.2010.537317) Table 3: all adults 18-80",
         "not_held_reason": ("Europe PMC: not open access; Unpaywall: no open location (evidence/acquisition_cascade/ATTEMPTS.jsonl, "
                             "target Wade2011). The values are RELAYED by the orchestrating lane (melatonin review 36c127c4) and are "
                             "not verified against held bytes."),
         "relayed_value": {"mean1": -14.6, "sd1": 43.9, "nc1": 360, "mean2": -7.9, "sd2": 50.9, "nc2": 362},
         "value": None},
        {"version_id": "v1b-2011-aged-55-80", "kind": "COMPANION_REPORT", "date": "2011",
         "source": "Wade 2011 Table 3: aged 55-80", "not_held_reason": "as v1 (not openly held; relayed)",
         "relayed_value": {"mean1": -15.4, "sd1": 44.4, "nc1": 294, "mean2": -5.5, "sd2": 43.2, "nc2": 284},
         "value": None}],
    "governing": {"state": "PENDING", "version_id": "v0-2010-subgroup-65-80", "reason": (
        "the protocol adopted the pre-specified 65-80 subgroup as the disclosed analysis population; the companion report "
        "gives the all-adult 18-80 result (the protocol's population is 'adults with primary insomnia'), but it is not "
        "openly held, so it cannot govern. Which analysis governs once it is held is a protocol decision owed to Mahmood.")}}]
open(sp, "w", encoding="utf-8", newline="\n").write(json.dumps(sv, indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- (4) Wade 2010 arm-label conflict
X = H + "Wade2010/PMC2933606.xml"
REG = H + "Wade2010-registration/NCT00397189.json"
conf = {"conflicts": [{
    "topic": SLUG, "trial_id": "PMID 20712869", "experimental_label": "melatonin",
    "what": "which arm owns n=394 and n=395 (and so every count in the safety tables) in Wade 2010",
    "arm_counts": [394, 395],
    "locations": [
        {"location": "publisher PDF, Table 8", "says": {"394": "placebo", "395": "melatonin"}, "held": False,
         "basis": ("relayed by the orchestrating lane (melatonin review 36c127c4); the BMC PDF location answered this lane a "
                   "3 KB non-PDF page (recorded, not retried)")},
        {"location": "publisher PDF, Table 9", "says": {"394": "melatonin", "395": "placebo"}, "held": False,
         "basis": "relayed by the orchestrating lane; not held (as above)"},
        {"location": "PMC XML, Table 8 (held)", "says": {"394": "melatonin", "395": "placebo"}, "held": True,
         "witness": W(X, "PRM Placebo PRM Placebo No. of patients 394 395 534 177")},
        {"location": "PMC XML, Table 9 (held)", "says": {"394": "melatonin", "395": "placebo"}, "held": True,
         "witness": W(X, "Placebo( n = 395)")}],
    "corroboration": [
        {"source": "ClinicalTrials.gov NCT00397189 posted results, participant flow (3-week period): Circadin STARTED 394, Placebo STARTED 395",
         "says": {"394": "melatonin", "395": "placebo"}, "independent_of_article": True,
         "witnesses": [RAW(REG, '"groups":[{"id":"FG000","title":"Circadin"', '"id":"FG001","title":"Placebo"'),
                       RAW(REG, '{"type":"STARTED","achievements":[{"groupId":"FG000","numSubjects":"394"}', '{"groupId":"FG001","numSubjects":"395"}')]},
        {"source": "ClinicalTrials.gov NCT00397189 posted results, adverse-event groups: Circadin at risk 394, Placebo at risk 395",
         "says": {"394": "melatonin", "395": "placebo"}, "independent_of_article": True,
         "witnesses": [RAW(REG, '{"id":"EG000","title":"Circadin"', '"seriousNumAtRisk":394')]},
        {"source": "PMC XML Table 9 (the SAME article in another format: identical counts, so it does not count)",
         "says": {"394": "melatonin", "395": "placebo"}, "independent_of_article": False}]}]}
open("docs/arm_label_conflicts.json", "w", encoding="utf-8", newline="\n").write(json.dumps(
    {"_doc": ("Arm-label source conflicts (harness/arm_label_conflict.py): every location, held or relayed, and the "
              "corroboration offered; adjudication is COMPUTED (only a source independent of the article can settle it) "
              "and nothing is auto-flipped. Recorded by the evidence lane (Claude Opus 5.5), 2026-09-28."), **conf},
    indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- (5) Luthringer: reported, extraction pending
LSPAN = "By the end of the double-blind treatment, the PRM group had significantly shorter sleep onset latency (9 min; P = 0.02) compared with the placebo group"
RSPAN = "randomized double-blind to PRM or placebo (3 weeks) followed by withdrawal period (3 weeks)"
ab = recs["19584739"]["abstract"]
assert LSPAN in ab and RSPAN in ab
vep = f"cache/{SLUG}/verified_effects.json"
raw_e = open(vep, encoding="utf-8").read()
ve = json.loads(raw_e)
rows = ve.get("19584739") or []
rows = rows if isinstance(rows, list) else [rows]
rows = [r for r in rows if r.get("outcome") != "Sleep-onset latency"] + [{
    "outcome": "Sleep-onset latency", "kind": "typed_refusal", "provenance": "REFUSED_ON_EVIDENCE",
    "document_ref": REC, "document_sha256": sha(REC), "source_span": LSPAN, "reported_unresolved_span": LSPAN,
    "randomised_period_span": RSPAN,
    "reason": ("Outcome reported; analysis-ready extraction pending. The randomised treatment is 3 weeks (a single-blind "
               "placebo run-in precedes it and a withdrawal period follows); the abstract gives the between-group "
               "difference (9 min; P = 0.02) without per-arm means or SDs, and none is imputed.")}]
ve["19584739"] = rows
open(vep, "w", encoding="utf-8", newline="\n").write(json.dumps(ve, indent=1 if raw_e.startswith('{\n "') else 2, ensure_ascii=False) + ("\n" if raw_e.endswith("\n") else ""))
print("melatonin: companions, Lemoine pooled report, Wade SOL chain (PENDING), arm-label conflict, Luthringer row")
