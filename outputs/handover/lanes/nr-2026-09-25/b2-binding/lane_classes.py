"""Lane NR's classification of every departing membership by the BINDING constraint that failed P5, written BEFORE
the blind codex classification (NR-C02) was run. Hand labels are from the executed re-runs in
contrast_cases.json / entry_population.json (the derivation code re-run on the held rows)."""
import json
from pathlib import Path

rows = json.loads(Path(r"C:/mh-lanes/nr/work/departing_evidence.json").read_text(encoding="utf-8"))

# INTERVENTION_CONTRAST_NOT_PROVEN, by family (derivation re-run: 0 contrasts for all 18)
CONTRAST = {
    "NCT00439777": ("ACTIVE_COMPARATOR", "rivaroxaban vs enoxaparin/VKA: the derivation records a contrast only when the arms differ by the agent alone"),
    "NCT00986154": ("ACTIVE_COMPARATOR", "edoxaban+heparin vs heparin+warfarin: the non-agent sets differ (warfarin)"),
    "NCT00262600": ("ACTIVE_COMPARATOR", "dabigatran vs warfarin (RE-LY)"),
    "NCT00403767": ("ACTIVE_COMPARATOR", "rivaroxaban vs warfarin (ROCKET AF)"),
    "NCT00412984": ("ACTIVE_COMPARATOR", "apixaban vs warfarin (ARISTOTLE; arm labels '1','2' but linked interventions complete)"),
    "NCT00781391": ("ACTIVE_COMPARATOR", "edoxaban vs warfarin (ENGAGE AF)"),
    "NCT02468232": ("ACTIVE_COMPARATOR", "LCZ696 vs enalapril"),
    "NCT01035255": ("ACTIVE_COMPARATOR", "LCZ696 vs enalapril (PARADIGM-HF)"),
    "NCT00391872": ("ACTIVE_COMPARATOR", "ticagrelor vs clopidogrel (PLATO)"),
    "NCT01294462": ("ACTIVE_COMPARATOR", "ticagrelor+ASA vs clopidogrel+ASA"),
    "NCT02875873": ("ACTIVE_COMPARATOR", "Plasma-Lyte vs saline 0.9% (both crossed with infusion speed)"),
    "NCT00973154": ("CONTROL_CODED_AS_ACTIVE", "the placebo arm's linked intervention is 'prednisone' in the held registry rows"),
    "NCT04348305": ("CONTROL_CODED_AS_ACTIVE", "isotonic saline control linked as active 'sodium chloride 9mg/ml'"),
    "NCT03036462": ("CONTROL_CODED_AS_ACTIVE", "saline control linked as active 'saline'; the verum arm's linked name is 'iron', not an agent term"),
    "NCT02104817": ("CONTROL_CODED_AS_ACTIVE", "corn-oil control linked as active 'corn oil control'"),
    "NCT01703208": ("LEXICON_GAP", "omarigliptin (a DPP-4 inhibitor) is not in the topic's agent list"),
    "NCT01492361": ("LEXICON_GAP", "AMR101 (icosapent ethyl) is not matched by the omega-3 agent terms"),
    "NCT00127452": ("NOT_DERIVABLE_FROM_ARMS", "every arm's linked intervention is 'margarine spread'; the fatty-acid contrast is not in the arm rows"),
}
# ENTRY_POPULATION_NOT_ESTABLISHED, by family: held registry conditions vs protocol population_any (substring test)
ENTRY = {
    "NCT03334604": ("WILDCARD_NOT_HONOURED", "conditions 'Antibiotic-associated Diarrhea'; protocol term 'antibiotic-associated diarr*' is tested as a literal substring"),
    "NCT05607056": ("WILDCARD_NOT_HONOURED", "conditions 'Antibiotic-associated Diarrhea'; protocol term 'antibiotic-associated diarr*' is tested as a literal substring"),
    "NCT01897532": ("TERM_FORM_MISMATCH", "conditions 'Diabetes Mellitus, Type 2' vs term 'type 2 diabetes'"),
    "NCT01131676": ("TERM_FORM_MISMATCH", "conditions 'Diabetes Mellitus, Type 2' vs terms 'type 2 diabetes (mellitus)'"),
    "NCT01730534": ("TERM_FORM_MISMATCH", "conditions 'Diabetes Mellitus, Non-Insulin-Dependent' (a type 2 synonym)"),
    "NCT02422186": ("TERM_FORM_MISMATCH", "conditions 'Depressive Disorder, Treatment-Resistant' vs 'treatment-resistant depression'"),
    "NCT03434041": ("TERM_FORM_MISMATCH", "conditions 'Depressive Disorder, Treatment-Resistant' vs 'treatment-resistant depression'"),
    "NCT03030235": ("TERM_FORM_MISMATCH", "conditions 'Chronic Heart Failure With Preserved Systolic Function' vs 'preserved ejection fraction'"),
    "NCT00643201": ("TERM_FORM_MISMATCH", "conditions 'Venous Thrombosis' vs 'venous thromboembolism' / 'deep vein thrombosis'"),
    "NCT00291330": ("CONDITIONS_TOO_GENERAL", "conditions 'Thromboembolism'; venous not stated in the conditions field"),
    "NCT00680186": ("CONDITIONS_TOO_GENERAL", "conditions 'Thromboembolism'; venous not stated in the conditions field"),
    "NCT00089791": ("CONDITIONS_TOO_GENERAL", "conditions 'Osteoporosis'; postmenopausal is in the criteria, not the conditions field"),
    "NCT02465515": ("CONDITIONS_TOO_GENERAL", "conditions 'Diabetes Mellitus'; type 2 not stated in the conditions field"),
    "NCT02721654": ("CONDITIONS_DIFFER", "conditions 'Hypovolemia' vs a critically-ill / ICU population"),
    "NCT00471640": ("CONDITIONS_TOO_GENERAL", "conditions 'Pneumonia' vs community-acquired pneumonia"),
    "NCT04381936": ("CONDITIONS_DIFFER", "conditions 'Pneumonia' vs COVID-19 (RECOVERY's registry conditions)"),
    "NCT01764633": ("CONDITIONS_DIFFER", "conditions 'Dyslipidemia' vs atherosclerotic cardiovascular disease"),
    "NCT03574597": ("CONDITIONS_DIFFER", "conditions 'Overweight','Obesity' vs overweight/obesity WITH cardiovascular disease"),
}
out = []
for r in rows:
    code, fam = r["code"], r["family"]
    if code == "INTERVENTION_CONTRAST_NOT_PROVEN":
        cls, why = CONTRAST[fam]
    elif code == "ENTRY_POPULATION_NOT_ESTABLISHED":
        cls, why = ENTRY[fam]
    elif code == "REGISTRY_PARENT_UNRESOLVED":
        cls, why = "NO_REGISTRY_PARENT_LINKED", "a synthetic family: no registry record is linked to the report"
    elif code == "INSUFFICIENT_PICD_EVIDENCE":
        cls, why = "NON_CTGOV_REGISTRY", f"{fam}: the P5 design/conditions/arms test reads AACT (ClinicalTrials.gov) rows only"
    else:
        cls, why = "INELIGIBLE_ON_HELD_EVIDENCE", "INELIGIBLE (with the held-source conflict the audit records)"
    out.append(dict(r, lane_class=cls, lane_basis=why))
Path(r"C:/mh-lanes/nr/work/lane_classes.json").write_bytes(json.dumps(out, ensure_ascii=False, indent=1).encode())
import collections
print(collections.Counter(o["lane_class"] for o in out))
