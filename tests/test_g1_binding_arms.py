"""Plants (codex binding-v8-fe3ed2a7 g1#1-2, reproduced): a placebo matched to a DOSED drug read as the intervention
arm; a usual-care control with a bracketed abbreviation read as an identifiable active drug (an unsupported exclusion)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from g1_binding_aact import arm_role  # noqa: E402
from g1_binding_enumerate import arm_scope  # noqa: E402


def test_a_placebo_matched_to_a_dosed_drug_is_the_control():
    assert arm_role("Placebo to match 56 mg esketamine", ["esketamine"]) == "control"
    assert arm_role("Esketamine 56 mg + oral antidepressant", ["esketamine"]) == "intervention"
    assert arm_role("Placebo for esketamine + oral antidepressant", ["esketamine"]) == "control"


def test_usual_care_with_an_abbreviation_is_not_an_active_drug():
    assert arm_scope([{"drug": "esketamine"}, {"drug": "Usual care (TAU)"}], ["esketamine"], ["placebo"]) == "UNRESOLVED"
    assert arm_scope([{"drug": "esketamine"}, {"drug": "Quetiapine XR"}], ["esketamine"], ["placebo"]) == "OUT_OF_SCOPE:COMPARATOR_NOT_PLACEBO"
