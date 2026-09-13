"""Heterogeneity narratives must be DERIVED from the actual pooled endpoint, not authored (audit 24): a
KIDNEY/renal composite must not be described with CV-MACE components (HF hospitalization, revascularization),
which invented an 'HF hospitalization' narrative on the sglt2-ckd and finerenone pools by catching a secondary
CV outcome in the same abstract. It must name the kidney threshold/definition differences it actually pools."""
from harness import extract


def test_kidney_composite_names_kidney_components_not_cv():
    dapa = "The primary composite outcome was a sustained decline of at least 50% in eGFR, end-stage kidney disease, or death from renal or cardiovascular causes. Heart failure hospitalization was a secondary outcome."
    empa = "The primary outcome was progression of kidney disease (a sustained >=40% decrease in eGFR or end-stage kidney disease) or death from cardiovascular causes."
    note = extract.composite_heterogeneity("CKD progression / kidney composite outcome", [dapa, empa])
    assert note, "differing kidney thresholds should be disclosed"
    assert "HF hospitalization" not in note, "a kidney composite must not name CV-MACE components"
    assert "eGFR" in note, "the kidney-threshold heterogeneity must be named"


def test_cv_mace_composite_still_uses_cv_vocabulary():
    colcot = "The primary end point was a composite of cardiovascular death, myocardial infarction, stroke, or urgent hospitalization for angina leading to revascularization."
    lodoco = "The composite primary end point was cardiovascular death, myocardial infarction, or ischemic stroke."
    note = extract.composite_heterogeneity("MACE composite", [colcot, lodoco])
    assert note and "revascularization" in note, "a CV-MACE composite must still name CV components"
