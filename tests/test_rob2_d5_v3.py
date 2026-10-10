"""D5 v3 (reviews 18 + 25): an unknown component is never a match; D5 is judged on the trial's SELECTED endpoint
(registered title it is bound to, or its role 'primary end point'), factor-aware in factorial trials; 'not
established', never 'possibly post hoc'. Fixed strings copied from the registry records the auditors cite."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import rob2  # noqa: E402

TARGET = "Composite cardiovascular death or hospitalisation for heart failure"
R18 = {"broader_registered_primary": "Subjects Included in the Composite Endpoint of CV Death, Hospitalization Due to "
                                     "Heart Failure or Urgent Visit Due to Heart Failure.",
       "selected_registered_secondary": "Subjects Included in the Composite Endpoint of CV Death or Hospitalization Due "
                                        "to Heart Failure.",
       "synthetic_unstable_angina_extra_component": "Subjects Included in the Composite Endpoint of CV Death, "
                                                    "Hospitalization Due to Heart Failure or Unstable Angina."}


def test_PLANT_r18_urgent_hf_visit_is_a_component_so_the_broad_primary_is_not_the_selected_secondary():
    m = {k: rob2.outcome_match_v3(TARGET, {"measure": v})["matched"] for k, v in R18.items()}
    assert m == {"broader_registered_primary": False, "selected_registered_secondary": True,
                 "synthetic_unstable_angina_extra_component": False}


def test_PLANT_r18_an_unrecognised_cardiovascular_component_is_not_established_never_a_match():
    d = rob2.outcome_match_v3("Composite of cardiovascular death, myocardial infarction or stroke",
                              {"measure": "Composite of cardiovascular death, myocardial infarction, stroke or "
                                          "peripheral amputation"})
    assert d["matched"] is None and d["registered_unrecognised"] == ["peripheral amputation"]
    # qualifiers and abbreviations are not components
    assert rob2.cardio_unrecognised("Major Adverse Cardiovascular Events (MACE) Composite of Cardiovascular (CV) Death, "
                                    "Non-Fatal Myocardial Infarction (MI), and Non-Fatal Stroke as adjudicated by the "
                                    "event adjudication committee") == ()
    # a VTE composite is not judged by the cardiovascular vocabulary
    assert rob2.cardio_unrecognised("Composite of recurrent deep vein thrombosis, non-fatal pulmonary embolism or "
                                    "VTE-related death") == ()


CLEAR_PRIM = [
    {"measure": "Major Adverse Cardiac Events (MACE)", "description": "Major Adverse Cardiac Events (MACE) for SYNERGY "
     "Stent (defined as the composite of death, recurrent target vessel MI, stroke, or ischemia driven target vessel "
     "revascularization) compared to performance goal"},
    {"measure": "Composite of cardiovascular death, recurrent myocardial infarction, stroke, or unplanned ischemia "
                "driven revascularization", "description": "colchicine versus placebo"},
    {"measure": "Composite of cardiovascular death, new or worsening heart failure, recurrent myocardial infarction, or "
                "stroke (co-primary 2)", "description": "spironolactone versus placebo"},
]
CLEAR_SEL = {"pooled_outcome": "Trial-defined major coronary/cardiovascular composite", "registered_title": None,
             "role": "primary", "our_terms": ["colchicine"],
             "other_factor_terms": ["SYNERGY Bioabsorbable Polymer Drug-Eluting Stent", "Spironolactone"]}


def test_PLANT_r25_clear_is_judged_on_the_colchicine_factor_primary():
    d = rob2.derive_d5_v3(CLEAR_PRIM, [], CLEAR_SEL)
    assert d["level"] == "low" and "unplanned ischemia driven revascularization" in d["basis"]
    assert sorted(d["inputs"]["factor_excluded_outcomes"])[0].startswith("Composite of cardiovascular death, new or")
    # without the factor filter the colchicine HR could be 'verified' against another factor's outcome
    no_filter = rob2.derive_d5_v3(CLEAR_PRIM, [], dict(CLEAR_SEL, other_factor_terms=[]))
    assert no_filter["level"] != "low"                       # three primaries: the role alone cannot pick one


def test_PLANT_r25_colcot_primary_by_role_never_its_cardiac_arrest_secondary():
    prim = [{"measure": "First Event of Cardiovascular Death, Resuscitated Cardiac Arrest, Acute Myocardial "
                        "Infarction, Stroke, or Urgent Hospitalization for Angina Requiring Coronary Revascularization"}]
    sec = [{"measure": "First Event of Cardiovascular Death, Resuscitated Cardiac Arrest, Acute MI or Stroke."}]
    sel = {"pooled_outcome": "Major adverse cardiovascular events", "registered_title": None, "role": "primary",
           "our_terms": ["colchicine"], "other_factor_terms": []}
    d = rob2.derive_d5_v3(prim, sec, sel)
    assert d["level"] == "low" and d["inputs"]["comparison"]["method"] == "role_primary"
    # and 3-point MACE is NOT the cardiac-arrest secondary (v2 dropped 'resuscitated cardiac arrest')
    assert rob2.outcome_match_v3("Major adverse cardiovascular events", sec[0])["matched"] is False


def test_PLANT_never_possibly_post_hoc_and_the_basis_names_the_trigger():
    d = rob2.derive_d5_v3([{"measure": "Major Bleeding"}], [], {"pooled_outcome": "All-cause mortality",
                                                                 "registered_title": None, "role": None})
    assert d["level"] == "some concerns" and "post-hoc" not in d["basis"] and "post hoc" not in d["basis"]
    assert d["basis"].startswith("registered-outcome identity not established")


def test_v3_domains_rederive_from_their_own_inputs():
    d = rob2.derive_d5_v3(CLEAR_PRIM, [], CLEAR_SEL)
    again = rob2.rederive_domain(d)
    assert (again["level"], again["basis"]) == (d["level"], d["basis"])


def test_PLANT_one_other_active_intervention_is_a_comparator_not_a_factor(monkeypatch, tmp_path):
    import json
    import rob2_build as rb
    (tmp_path / "topics").mkdir()
    (tmp_path / "topics" / "t.json").write_text(json.dumps({"intervention_terms": ["edoxaban"],
                                                            "comparator_terms": ["warfarin"]}), encoding="utf-8")
    monkeypatch.setattr(rb, "ROOT", str(tmp_path))
    monkeypatch.setattr(rb, "INTERVENTIONS", {"NCT1": [("Edoxaban", "DRUG"), ("Warfarin", "DRUG"), ("Heparin", "DRUG")],
                                              "NCT2": [("Colchicine", "DRUG"), ("Spironolactone", "DRUG"),
                                                       ("SYNERGY Stent", "DEVICE"), ("Placebo", "DRUG")]})
    assert rb.factor_terms("t", ["NCT1"])[1] == []                     # heparin alone: background, not a factor
    assert rb.factor_terms("t", ["NCT2"])[1] == ["Colchicine", "SYNERGY Stent", "Spironolactone"]
