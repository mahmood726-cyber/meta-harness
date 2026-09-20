"""Three pooled states kept apart, and two checks computable from a served review.json alone. ODYSSEY OUTCOMES (pcsk9-mace,
PMID 30403574) is the positive control, pinned here as the row's exact served fields on 2026-09-20 (a control is pinned; the live
row will change when the pool is corrected)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pooled_class_sweep as pcs  # noqa: E402

TARGET = {"cardiovascular death", "myocardial infarction", "stroke"}
ODYSSEY = {"id": "PMID 30403574", "target_endpoint_class": "NEAR_MATCH", "endpoint_admissibility": "NEAR_MATCH_DECLARED",
           "endpoint_binding": "named_endpoint_resolved_to_definition_span",
           "target_endpoint_components": "['coronary heart disease death', 'myocardial infarction', 'stroke', 'unstable angina']",
           "target_endpoint_extra_components": "['unstable angina']", "target_endpoint_missing_components": "[]"}
FOURIER = {"id": "PMID 28304224", "target_endpoint_class": "EXACT_TARGET", "endpoint_admissibility": "EXACT_TARGET", "endpoint_binding": "registry_outcome_measure",
           "target_endpoint_components": "['cardiovascular death', 'myocardial infarction', 'stroke']",
           "target_endpoint_extra_components": "[]", "target_endpoint_missing_components": "[]"}
UNBOUND = {"id": "PMID 41211925", "target_endpoint_class": None, "endpoint_admissibility": "UNBOUND_LEGACY", "endpoint_binding": "unbound_legacy",
           "target_endpoint_components": None, "target_endpoint_extra_components": None, "target_endpoint_missing_components": None}


def test_three_pooled_states_are_never_alike():
    assert pcs.pooled_state(FOURIER) == "EXACT_TARGET_POOLED"
    assert pcs.pooled_state(ODYSSEY) == "NEAR_MATCH_POOLED"
    assert pcs.pooled_state(UNBOUND) == "UNBOUND_POOLED"


def test_odyssey_hits_c1_and_c2_and_fourier_hits_nothing():
    c = pcs.check_row(ODYSSEY, TARGET, TARGET)
    assert c["C1_extra_components_in_pooled_row"] is True and c["extra_components"] == ["unstable angina"]
    assert c["C2_missing_components_inconsistent"] is True and c["row_lacks"]["exact_rows_union"] == ["cardiovascular death"]
    assert c["row_surplus"]["exact_rows_union"] == ["coronary heart disease death", "unstable angina"]
    f = pcs.check_row(FOURIER, TARGET, TARGET)
    assert not f["C1_extra_components_in_pooled_row"] and not f["C2_missing_components_inconsistent"] and not f["C3_extra_components_inconsistent"]
    u = pcs.check_row(UNBOUND, TARGET, TARGET)
    assert not u["C1_extra_components_in_pooled_row"] and not u["C2_missing_components_inconsistent"]      # nothing to compare: not a clear


def test_c3_names_the_lexicon_collapse_not_the_row():
    """sacubitril NCT02468232: the row names the full composite; the lexicon reads the target name as one component. C3 fires
    against the lexicon target and NOT against the union of EXACT rows -- the discrepancy is in the target, and it is printed."""
    row = {"target_endpoint_class": "EXACT_TARGET", "target_endpoint_components": "['cardiovascular death', 'heart failure hospitalization']",
           "target_endpoint_extra_components": "[]", "target_endpoint_missing_components": "[]"}
    c = pcs.check_row(row, {"cardiovascular death"}, {"cardiovascular death", "heart failure hospitalization"})
    assert c["C3_extra_components_inconsistent"] is True and c["row_surplus"] == {"lexicon_canonical": ["heart failure hospitalization"], "exact_rows_union": []}
    assert c["C2_missing_components_inconsistent"] is False


def test_sweep_over_the_served_state():
    out = pcs.sweep("316d2e48")
    assert out["reviews"] == 32 and out["pooled_rows"] == 147
    assert out["by_pooled_state"] == {"UNBOUND_POOLED": 121, "EXACT_TARGET_POOLED": 25, "NEAR_MATCH_POOLED": 1}
    assert [(h["slug"], h["trial"]) for h in out["C1_hits"]] == [("pcsk9-mace", "PMID 30403574")]
    assert [(h["slug"], h["trial"]) for h in out["C2_hits"]] == [("pcsk9-mace", "PMID 30403574")]
    assert {(m["slug"]) for m in out["pools_mixing_states"] if "NEAR_MATCH_POOLED" in m["states"]} == {"pcsk9-mace"}
