"""DOAC-VTE review (hash 5f9c2b44): explicit scope decisions for J-EINSTEIN and BOTTICELLI from the PROTOCOL'S OWN TEXT,
their known-eligible-missing entries with witnessed result states, and Hokusai-VTE's major-bleeding typed refusal
restated against the held FDA label (the old reason was true only of the abstract).
  python outputs/handover/doac_sources/make_scope_and_states.py"""
import hashlib, json

sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
SLUG = "doac-vte-recurrence"
PRIM = "Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)"
JE = "evidence/acquisition_cascade/held/J-EINSTEIN/PMC4339301.xml"
BO = "evidence/acquisition_cascade/held/BOTTICELLI/europepmc_record_18541000.json"
LABEL = "outputs/handover/doac_sources/fda_savaysa_label_2023-10.txt"


def W(p, s):
    return {"path": p, "sha256": sha(p), "span": s}


def crit(rule, span, ev=None, met=True):
    return {"rule": rule, "protocol_span": span, **({"evidence": ev} if ev else {}), "met": met}


# ---------------------------------------------------------------- scope decisions (protocol text only)
scope = {
    "search_limitation": ("the committed search queries the six pivotal PubMed UIDs named in the protocol's Search section "
                          "(the six phase-3 trials of the comparator's pooled analysis); trials eligible by the protocol's "
                          "own I1-I4 but outside those UIDs are not reached by the search: J-EINSTEIN and BOTTICELLI"),
    "decisions": [
        {"trial": "J-EINSTEIN DVT and PE program", "ids": ["PMID 25717286", "NCT01516840", "NCT01516814"],
         "decision": "ELIGIBLE",
         "basis": ("the protocol's own I1-I4 are met; one programme with two registrations (DVT and PE), counted as ONE "
                   "trial; 100 randomised 81:19, 3 rivaroxaban patients from one site excluded for GCP non-compliance"),
         "not_a_reason": "absence from the comparator's six-trial list is a search limitation, not an exclusion",
         "outcome_note": ("symptomatic recurrent VTE 1/78 vs 0/19 is this review's outcome; 1/78 vs 1/19 is the BROADER "
                          "symptomatic-or-asymptomatic-deterioration composite and is not used"),
         "criteria": [
             crit("I1", "**I1** - randomised controlled trial",
                  W(JE, "a total of 100 patients with DVT and/or PE were randomized at 39 sites")),
             crit("I2", "**I2** - population is adults with acute symptomatic VTE, DVT, and/or PE",
                  W(JE, "Oral rivaroxaban for Japanese patients with symptomatic venous thromboembolism")),
             crit("I3", "**I3** - dabigatran, rivaroxaban, apixaban, edoxaban, or a DOAC/NOAC as the randomised intervention",
                  W(JE, "81 patients were assigned to receive rivaroxaban")),
             crit("I4", "**I4** - warfarin / VKA / conventional anticoagulant therapy comparator",
                  W(JE, "UFH/warfarin"))]},
        {"trial": "BOTTICELLI DVT", "ids": ["PMID 18541000"], "decision": "ELIGIBLE",
         "basis": ("the protocol's own I1-I4 are met: randomised; symptomatic DVT; apixaban; LMWH followed by a VKA "
                   "(the protocol's comparator explicitly includes initial parenteral anticoagulation followed by VKA). "
                   "Dose-ranging (three apixaban regimens) and phase 2 are pooling questions, not protocol exclusions"),
         "not_a_reason": "phase 2 / dose-ranging / absence from the comparator's six-trial list are not in the protocol's X1-X5",
         "outcome_note": ("17/358 vs 5/118 is the composite of symptomatic recurrent VTE AND asymptomatic imaging "
                          "deterioration, broader than this review's symptomatic recurrent VTE; three apixaban arms"),
         "criteria": [
             crit("I1", "**I1** - randomised controlled trial", W(BO, "randomized to receive 84-91 days of apixaban")),
             crit("I2", "**I2** - population is adults with acute symptomatic VTE, DVT, and/or PE",
                  W(BO, "Consecutive patients with symptomatic deep vein thrombosis were included")),
             crit("I3", "**I3** - dabigatran, rivaroxaban, apixaban, edoxaban, or a DOAC/NOAC as the randomised intervention",
                  W(BO, "apixaban 5 mg twice-daily, 10 mg twice-daily, or 20 mg once-daily")),
             crit("I4", "including initial parenteral anticoagulation followed by VKA",
                  W(BO, "low molecular weight heparin (LMWH) followed by a vitamin K antagonist (VKA)"))]},
    ],
}
sd_path = "docs/scope_decisions.json"
try:
    sd = json.load(open(sd_path, encoding="utf-8"))
except FileNotFoundError:
    sd = {"_doc": ("Scope decisions from the PROTOCOL'S OWN TEXT (harness/scope_decision.py): every rule span must occur "
                   "verbatim in protocols/<slug>.md; evidence spans are re-verified; a basis citing a comparator's trial "
                   "list is refused."), "topics": {}}
sd["topics"][SLUG] = scope
open(sd_path, "w", encoding="utf-8", newline="\n").write(json.dumps(sd, indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- known-eligible-missing entries
kp = "docs/known_eligible_missing.json"
raw = open(kp, encoding="utf-8").read()
kem = json.loads(raw)
rows = [r for r in kem["topics"].get(SLUG, []) if r.get("trial") not in ("J-EINSTEIN", "BOTTICELLI")]
rows += [
    {"trial": "J-EINSTEIN", "pmid": "25717286", "nct": "NCT01516840", "also_registered_as": ["NCT01516814"],
     "mechanism": "search limitation (the search queries the comparator's six pivotal UIDs); eligible by protocol I1-I4",
     "status": "source_held", "acquisition": {"route": "acquisition cascade: Europe PMC OA PMC4339301 (CC BY) + erratum PMC4877730",
                                              "held_path": JE, "held_sha256": sha(JE)},
     "comparisons": "one programme, two registrations (DVT NCT01516840, PE NCT01516814): ONE trial",
     "design_note": "100 randomised 81:19; 3 rivaroxaban patients from one site excluded for GCP non-compliance; 78 vs 19 analysed",
     "result_states": {PRIM: {
         "state": "EXTRACTED_NOT_ADMITTED",
         "span": ("A single patient in the rivaroxaban group (1/78; 1.4%) developed symptomatic recurrent VTE compared "
                  "with none of the 19 patients allocated to control treatment"),
         "witness": W(JE, "A single patient in the rivaroxaban group (1/78; 1.4%) developed symptomatic recurrent VTE "
                          "compared with none of the 19 patients allocated to control treatment"),
         "basis": ("1/78 vs 0/19 held; not admitted: outside the committed search. The erratum corrects this cell's "
                   "'1.4%' to '1.3%' (per cell; docs/source_versions.json); 1/78 vs 1/19 is the broader composite")}}},
    {"trial": "BOTTICELLI", "pmid": "18541000",
     "mechanism": "search limitation (the search queries the comparator's six pivotal UIDs); eligible by protocol I1-I4",
     "status": "source_held_abstract", "acquisition": {"route": "acquisition cascade: Europe PMC record with abstract (not OA)",
                                                       "held_path": BO, "held_sha256": sha(BO)},
     "design_note": "dose-ranging: apixaban 5 mg bid, 10 mg bid, 20 mg od vs LMWH/VKA; 520 included",
     "result_states": {PRIM: {
         "state": "REPORTED_UNRESOLVED",
         "span": "The primary outcome occurred in 17 of the 358 apixaban-treated patients",
         "witness": W(BO, "The primary efficacy outcome was the composite of symptomatic recurrent venous thromboembolism "
                          "and asymptomatic deterioration of bilateral compression ultrasound or perfusion lung scan"),
         "basis": ("17/358 vs 5/118 counts symptomatic recurrent VTE PLUS asymptomatic imaging deterioration -- broader "
                   "than this review's outcome; the symptomatic-only split is not in the held abstract; three dose arms")}}},
]
kem["topics"][SLUG] = rows
open(kp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(kem, indent=1 if raw.startswith('{\n "') else 2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""))

# ---------------------------------------------------------------- Hokusai major bleeding: the refusal restated
vp = "cache/doac-vte-recurrence/verified_effects.json"
vraw = open(vp, encoding="utf-8").read()
ve = json.loads(vraw)
rowsv = ve["23991658"]
old = next(r for r in rowsv if r["outcome"] == "Major bleeding")
new = {"outcome": "Major bleeding", "kind": "typed_refusal", "provenance": "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH",
       "source_level": 1, "document_ref": LABEL, "source_span": "Major Bleedingb, n (%) 56 (1.4) 66 (1.6)",
       "reason": ("Hokusai-VTE major bleeding IS reported: 56/4,118 edoxaban vs 66/4,122 warfarin, on treatment (during or "
                  "within three days of stopping), in the FDA label's Table 6.3 (held, public domain). This review's "
                  "major-bleeding estimand is the published HR and a count-derived RR is refused (as for AMPLIFY); the "
                  "published HR 0.84 (0.592-1.205) is in the sponsor's CSR erratum, which is not held "
                  "(docs/source_versions.json). The earlier refusal was true only of the abstract, which gives major and "
                  "clinically relevant non-major bleeding combined."),
       "supersedes": {k: old.get(k) for k in ("provenance", "reason", "document_ref")}}
ve["23991658"] = [new if r is old else r for r in rowsv]
open(vp, "w", encoding="utf-8", newline="\n").write(
    json.dumps(ve, indent=1 if vraw.startswith('{\n "') else 2, ensure_ascii=False) + ("\n" if vraw.endswith("\n") else ""))
print("scope decisions, known-missing entries and the Hokusai major-bleeding refusal written")
