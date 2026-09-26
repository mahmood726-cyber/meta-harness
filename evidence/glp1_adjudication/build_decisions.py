"""Result-level adjudication of FLOW, ELIXA and FREEDOM-CVO for glp1-ra-mace-t2d, against the protocol's explicit rules
(protocols/glp1-ra-mace-t2d.md at commit b10c53d3). Writes one decision file per trial in this directory.

Every witness is cut from textrep.render(<held file>) by a start anchor and an end anchor (never typed), asserted to be
a verbatim substring, and carries the file's sha256; protocol witnesses are also asserted verbatim in the file AS
COMMITTED at b10c53d3 (git show). Fails closed on any anchor that is missing or ambiguous. The decisions change
nothing served: admission to the primary pool is a served-number change, queued for Mahmood's signature.
  python evidence/glp1_adjudication/build_decisions.py"""
import datetime, hashlib, json, os, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "evidence", "scripts"))
import textrep  # noqa: E402

PROTO_REF, PROTO_COMMIT = "protocols/glp1-ra-mace-t2d.md", "b10c53d3783facb7e630219f0bb447fe6e22843e"
LABEL = "outputs/handover/glp1_regulatory/held/209637s025lbl.pdf"
STATR = "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf"
BRIEF = "outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf"
_cache = {}


def _render(ref):
    if ref not in _cache:
        _cache[ref] = textrep.render(ref)
    return _cache[ref]


def _sha(ref):
    return hashlib.sha256(open(os.path.join(ROOT, ref), "rb").read()).hexdigest()


def W(ref, start, end, occurrence=1):
    """Witness: the render text from the n-th occurrence of `start` through the first `end` after it."""
    t = _render(ref)
    i = -1
    for _ in range(occurrence):
        i = t.find(start, i + 1)
        if i < 0:
            sys.exit(f"REFUSED: anchor not found in {ref}: {start[:60]!r}")
    j = t.find(end, i)
    if j < 0:
        sys.exit(f"REFUSED: end anchor not found in {ref}: {end[:60]!r}")
    span = t[i:j + len(end)]
    assert span in t
    w = {"ref": ref, "sha256": _sha(ref), "span": span}
    if ref == PROTO_REF:
        committed = subprocess.run(["git", "show", f"{PROTO_COMMIT}:{PROTO_REF}"], cwd=ROOT, capture_output=True,
                                   text=True, encoding="utf-8", check=True).stdout
        if span not in textrep._ws(committed):
            sys.exit("REFUSED: protocol span is not in the file as committed at b10c53d3")
        w["commit"] = PROTO_COMMIT
    return w


def P(start, end):
    return W(PROTO_REF, start, end)


RULES = {
    "eligibility_B_prime": P("**Eligibility (B-prime).** Parallel-group", "systematically ascertained**"),
    "named_trials": P("FLOW (semaglutide, T2D with CKD;", "never from a secondary meta-analysis."),
    "estimand": P("**Estimand.** Intention-to-treat effect", "prespecified randomised cardiovascular follow-up."),
    "effect_measure": P("**Effect measure.** The primary analysis pools **log-HRs only**", "do not enter the primary pool."),
    "timepoint": P("**Timepoint.** The trial's prespecified primary cardiovascular analysis", "never substitute for the primary analysis."),
    "agents": P("**Pre-specified list (intervention agents).**", "lixisenatide."),
    "no_meta_values": P("5 older meta-analyses -- **pointers only, never the number itself**", "traced to a level 1-4 source or refused)."),
}


def decision(trial, **kw):
    d = {"object": "RESULT_LEVEL_ADJUDICATION", "review": "glp1-ra-mace-t2d", "trial": trial,
         "protocol": {"ref": PROTO_REF, "commit": PROTO_COMMIT, "sha256_of_file": _sha(PROTO_REF)},
         "made_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "by": "Claude Opus 5.5, evidence lane evid/evidence-records (assignment: senior external review, forwarded by Mahmood)",
         "status": "DECIDED_BY_LANE -- admission to the primary pool is a served-number change: QUEUED for Mahmood's signature, not landed"}
    d.update(kw)
    return d


def main():
    out = {}
    out["FLOW"] = decision(
        "FLOW", nct="NCT03819153", pmid="38785209",
        eligibility={
            "decision": "ELIGIBLE -- CONVENTIONAL_GLP1RA (primary) strand",
            "rules": {
                "RCT, parallel, double-blind, placebo-controlled": W("evidence/held/registry/NCT03819153.json", "DESIGN: allocation RANDOMIZED", "OUTCOMES_ASSESSOR"),
                "adults with type 2 diabetes": W("evidence/held/registry/NCT03819153.json", "CONDITION: Diabetes Mellitus, Type 2", "Type 2"),
                "adults (age floor)": W("evidence/held/registry/NCT03819153.json", "ELIGIBILITY AGE/SEX: minimum age 18 Years", "18 Years"),
                "prespecified agent (semaglutide)": W("evidence/held/registry/NCT03819153.json", "ARM: Semaglutide [EXPERIMENTAL]", "for up to 5 years"),
                "placebo comparator": W("evidence/held/registry/NCT03819153.json", "ARM: Placebo [PLACEBO_COMPARATOR]", "placebo (semglutide)"),
                "3-point MACE prospectively specified (registry: the composite, and its components as the 'Confirmatory Secondary MACE Endpoint')": W("evidence/held/registry/NCT03819153.json", "RESULT OUTCOME 11 [SECONDARY]: Number of Participants From Time of Randomization to Time to First Occurrence of a Major Adverse Cardiovascular Event (MACE)", "CV Death"),
                "components named as the Confirmatory Secondary MACE Endpoint": W("evidence/held/registry/NCT03819153.json", "Individual Components of the Confirmatory Secondary MACE Endpoint: Non-fatal Myocardial Infarction", "Non-fatal Myocardial Infarction"),
                "protocol names FLOW eligible": RULES["named_trials"],
            },
            "why": "Adults with T2D and CKD, semaglutide 1 mg weekly vs placebo, randomised, masked (quadruple), parallel; 3-point MACE was a confirmatory secondary endpoint with EAC-adjudicated events, reported by the regulator in the trial's own results table. The population restriction to CKD narrows, but stays inside, 'adults with type 2 diabetes'; B-prime names FLOW eligible.",
        },
        bound_result={
            "endpoint": W(LABEL, "Composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke (time to first occurrence) 254 (14.4) 212 (12.0)", "0.0289"),
            "endpoint_identity": {
                "rule": "BY SOURCE ROW: the label's Table 10 row whose own label enumerates the three components; header, row label and event counts are verbatim in one row witness; never by the numbers",
                "row": W(LABEL, "Table 10: Analyses of the Primary and Secondary Endpoints and their Individual Components in FLOW Trial", "0.0289"),
                "table_header": "Table 10: Analyses of the Primary and Secondary Endpoints and their Individual Components in FLOW Trial",
                "row_label": "Composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke (time to first occurrence)",
                "label_term": None, "definition_source": "row_label",
                "events": {"semaglutide": 212, "placebo": 254}},
            "not_this_row (kidney composite, HR 0.76)": W(LABEL, "Composite Endpoint (≥ 50% sustained eGFR decline", "0.76 (0.66, 0.88) 0.0003"),
            "contrast": {"value": "semaglutide 1 mg once weekly vs placebo", "witness": W(LABEL, "Individual Components in FLOW Trial Placebo N=1766 (%) OZEMPIC 1 mg N=1767", "OZEMPIC 1 mg N=1767")},
            "population": {"value": "all randomised (1767 vs 1766 = 3,533 randomised)", "witness": W(LABEL, "A total of 3,533 patients were randomized", "median of 41 months.")},
            "analysis": {"value": "Cox proportional hazards, treatment as factor, stratified by baseline SGLT2-inhibitor use; time from randomisation (in-trial, end of study)",
                         "witness": W(LABEL, "1 Cox proportional hazards model with treatment as factor", "(yes or no)."),
                         "observation_period_witness": W(LABEL, "Figure 8. Cumulative incidence: Time to First Occurrence of MACE in FLOW Trial", "modelled as competing risk.")},
            "estimate": {"value": 0.82, "scale": "HR"}, "ci": {"value": [0.68, 0.98], "level": 0.95},
            "events": {"semaglutide": 212, "placebo": 254},
            "level_1_agreement": W("evidence/held/38785209/europepmc_core.json", "the risk of major cardiovascular events 18% lower", "0.029)"),
            "timepoint": {"value": "final analysis after early cessation recommended at a prespecified interim analysis (end of randomised, blinded follow-up; median 3.4 years)",
                          "witness": W("evidence/held/38785209/europepmc_core.json", "median follow-up was 3.4 years", "prespecified interim analysis.")},
            "note": "estimate, CI and events are witnessed by the `endpoint` row (one table row, level 2); the NEJM abstract (level 1, visible only after the 2026-09-25 renderer fix) gives the same 0.82 (0.68-0.98). The abstract's 'major cardiovascular events' is identified as the 3-point composite by the label row and the registry, not by the number.",
        },
        consequence="Enters the CONVENTIONAL_GLP1RA primary pool -> served-number change (k 8 -> 9 alone; 8 -> 10 with ELIXA). Queued for signature with the derived before -> after (BEFORE_AFTER.json).",
    )
    out["ELIXA"] = decision(
        "ELIXA", nct="NCT01147250", pmid="26630143",
        eligibility={
            "decision": "ELIGIBLE -- CONVENTIONAL_GLP1RA (primary) strand",
            "rules": {
                "RCT, parallel, double-blind, placebo-controlled; T2D after ACS": W(STATR, "titled “A randomized, double-blind, placebo-controlled, parallel-group, multicenter study", "Acute Coronary Syndrome event”"),
                "adults (age floor 30)": W("evidence/held/registry/NCT01147250.json", "ELIGIBILITY AGE/SEX: minimum age 30 Years", "30 Years"),
                "prespecified agent (lixisenatide) vs matched placebo": W("evidence/held/registry/NCT01147250.json", "ARM: Placebo [PLACEBO_COMPARATOR]", "up to end of treatment."),
                "3-point MACE prospectively specified (secondary; exact three components)": W(STATR, "secondary endpoints – time to first secondary MACE event", "fatal stroke)"),
                "protocol names ELIXA eligible; value from the regulatory record, never a meta-analysis": RULES["named_trials"],
            },
            "why": "Adults with T2D and a recent ACS, lixisenatide vs matched placebo, randomised, double-blind, parallel. Its primary endpoint is the 4-point MACE+; 3-point MACE ('CV death, non-fatal MI and non-fatal stroke') was a prespecified secondary endpoint, which satisfies B-prime's 'or its exact three components, prospectively specified'.",
        },
        bound_result={
            "identity_rule": "BY SOURCE ROW + THE DEFINITION OF ITS LABEL + EVENT COUNTS, never by matching numbers: the 3-point secondary and the 4-point primary are both printed as HR 1.02 (0.89, 1.17) in this review",
            "endpoint_identity": {
                "row": W(STATR, "Table 8: Analysis of the MACE Endpoint Placebo (N=3,034)", "400 (13.2%)"),
                "table_header": "Table 8: Analysis of the MACE Endpoint",
                "row_label": "MACE endpoint (on-study)",
                "label_term": "MACE",
                "definition": W(STATR, "secondary endpoints – time to first secondary MACE event", "fatal stroke)"),
                "events": {"lixisenatide": 400, "placebo": 392},
                "not_this_row": W(STATR, "Table 1: Pre-specified Analysis of Primary MACE+ Endpoint", "406 (13.4%)")},
            "endpoint": W(STATR, "3.3.4.3 Analyses of MACE ITT analyses (on-study and on-treatment) of MACE, defined as cardiovascular death, non-fatal MI, and non-fatal stroke", "with a point estimate of 1.02."),
            "not_this_row (4-point MACE+ primary: 399 vs 406, 1.017 (0.886, 1.168))": W(STATR, "Using the pre-specified Cox proportional hazards model, the hazard ratio estimate and associated 95% confidence interval is 1.017", "406 (13.4%)"),
            "contrast": {"value": "lixisenatide (10 mcg QD, then 20 mcg QD) vs matched placebo", "witness": W("evidence/held/registry/NCT01147250.json", "ARM: Lixisenatide [EXPERIMENTAL]", "up to end of treatment.")},
            "population": {"value": "ITT, all randomised (3,034 vs 3,034 = 6,068)", "witness": W(STATR, "A total of 6068 randomized subjects were included in the intent-to-treat population.", "intent-to-treat population.")},
            "analysis": {"value": "Cox proportional hazards, on-study (ITT) -- the prespecified end-of-follow-up analysis; on-treatment is a sensitivity",
                         "witness": W(STATR, "Table 8: Analysis of the MACE Endpoint Placebo (N=3,034)", "MACE endpoint (on-treatment) 1.01 (0.87, 1.17)")},
            "estimate": {"value": 1.02, "scale": "HR"}, "ci": {"value": [0.887, 1.172], "level": 0.95},
            "events": {"lixisenatide": 400, "placebo": 392},
            "source_conflict": "the same FDA review renders the on-study interval as (0.887, 1.172) in the text and as (0.89, 1.18) in Table 8; the unrounded text is bound (as ADJ-GLP1-005 proposed); both renderings were pooled and the conclusion is identical (BEFORE_AFTER.json)",
        },
        consequence="Enters the CONVENTIONAL_GLP1RA primary pool -> served-number change (k 8 -> 9 alone; 8 -> 10 with FLOW). Queued for signature.",
    )
    out["FREEDOM-CVO"] = decision(
        "FREEDOM-CVO", nct="NCT01455896", pmid="34873344",
        eligibility={
            "decision": "ELIGIBLE for GLP1RA_ANY_DELIVERY only; NOT in the CONVENTIONAL_GLP1RA primary pool -- settled by the protocol text, not UNRESOLVED",
            "rules": {
                "RCT, double-blind, placebo-controlled CVOT (placebo = the same device without exenatide)": W(BRIEF, "CLP-107 (FREEDOM) Phase 3, multicenter, randomized, double- blind, placebo- controlled, CVOT", "Comparator: ITCA 650 subdermal placebo"),
                "placebo device": W(BRIEF, "Study CLP-107 was a randomized, multicenter study to evaluate CV outcomes with ITCA 650", "(same device but without exenatide)."),
                "type 2 diabetes": W("evidence/held/registry/NCT01455896.json", "CONDITION: Type 2 Diabetes", "Type 2 Diabetes"),
                "adults (age floor 40)": W("evidence/held/registry/NCT01455896.json", "ELIGIBILITY AGE/SEX: minimum age 40 Years", "40 Years"),
                "delivery route: continuous subcutaneous osmotic mini-pump": W(BRIEF, "ITCA 650 is a subcutaneously implanted drug-device combination product containing an osmotic mini-pump", "over the life of the implant."),
                "PROTOCOL CLASS BOUNDARY (decides the strand)": RULES["agents"],
                "PROTOCOL: primary strand is CONVENTIONAL_GLP1RA, ANY_DELIVERY rendered alongside": RULES["named_trials"],
            },
            "approval_caveat": {
                "state": "PROTOCOL TEXT SETTLES IT; STRAND-PAIR APPROVAL NOT EVIDENCED BEYOND THE PROTOCOL REGISTRATION",
                "what": "the class-boundary decision document lists the glp1 strand pair under 'Proposed strand pairs (to Mahmood for approval before implementation)' (the SGLT2 pair in the same document is marked decided). The registered protocol (b10c53d3, under Mahmood's authority) does name the strands and place ITCA 650 on ANY_DELIVERY, so the call follows the protocol text; if Mahmood has NOT approved the glp1 strand pair, FREEDOM-CVO's delivery-route question reverts to UNRESOLVED and nothing else in this decision changes.",
                "witness": W("outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md", "## Proposed strand pairs (to Mahmood for approval before implementation)", "FREEDOM-CVO |"),
                "witness_scope": "the heading and the glp1 row it governs are one contiguous span in the rendered document"},
            "why": "The protocol's pre-specified agent list places 'ITCA 650 continuous subcutaneous delivery on the GLP1RA_ANY_DELIVERY strand', and names CONVENTIONAL_GLP1RA as the primary strand with ANY_DELIVERY rendered alongside. The delivery-route question is therefore answered by the protocol's own text: an osmotic-pump exenatide is NOT a conventional GLP-1 RA for the primary analysis. The protocol does not define 'conventional' beyond this placement; the placement itself is explicit, so no guess is needed and the call is not UNRESOLVED.",
        },
        bound_result={
            "endpoint": W(BRIEF, "3-Point MACE* 85/2075 (4.1%) 2.94 69/2081 (3.3%) 2.37 1.24 (0.90, 1.70)", "1.24 (0.90, 1.70)"),
            "table_context": W(BRIEF, "Table 19. Time to First Occurrence of 3-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke) and 4-Point MACE (CV Death, Nonfatal MI, Nonfatal Stroke, Unstable Angina) – ITT Population End of Study, FREEDOM (CLP-107) MACE Type", "FREEDOM (CLP-107) MACE Type", occurrence=1),
            "not_these_rows": {
                "4-point MACE (same table)": W(BRIEF, "4-Point MACE 95/2075 (4.6%) 3.29 79/2081 (3.8%) 2.72 1.21 (0.90, 1.63)", "1.21 (0.90, 1.63)"),
                "on-treatment 3-point 1.36 and pooled 4-point 1.12": W(BRIEF, "The range of HRs include HR=1.12 (95% CI: 0.84, 1.50)", "the individual endpoint of CV death."),
            },
            "contrast": {"value": "ITCA 650 (exenatide in DUROS: 20 mcg/day then 60 mcg/day, replaced every 26 weeks) vs ITCA 650 placebo device", "witness": W(BRIEF, "Subjects were randomized to the proposed to-be-marketed dosing regimen of ITCA 650", "(same device but without exenatide).")},
            "population": {"value": "ITT, FREEDOM (CLP-107) alone: 2,075 vs 2,081 randomised", "witness": W(BRIEF, "Randomized (%) 2075 (100.0) 2081 (100.0)", "2081 (100.0)")},
            "analysis": {"value": "CDER Cox proportional hazards; 'On-Study' (end-of-study) censoring = the protocol's end of randomised follow-up; FREEDOM alone (not pooled with CLP-103/105)",
                         "witness": W(BRIEF, "CDER assessed the results for the endpoint of the time to first occurrence of any event in the 3-point and 4-point MACE composite endpoints based only on events from CLP-107 (FREEDOM)", "1.21 (0.90, 1.63), respectively.")},
            "estimate": {"value": 1.24, "scale": "HR"}, "ci": {"value": [0.90, 1.70], "level": 0.95},
            "events": {"ITCA_650": 85, "placebo_device": 69},
        },
        consequence="Does NOT enter the primary (CONVENTIONAL_GLP1RA) pool: no primary served number changes. It enters the GLP1RA_ANY_DELIVERY strand the protocol says is rendered alongside (k 8 -> 11 with FLOW and ELIXA; BEFORE_AFTER.json). The served page does not yet render that strand; rendering it is a served-page change, also queued.",
    )
    for k, d in out.items():
        json.dump(d, open(os.path.join(os.path.dirname(__file__), f"{k}.json"), "w", encoding="utf-8", newline="\n"),
                  indent=1, ensure_ascii=False)
        n = sum(1 for _ in json.dumps(d).split('"span"')) - 1
        print(f"{k}: {d['eligibility']['decision']} | witnesses {n}")


if __name__ == "__main__":
    main()
