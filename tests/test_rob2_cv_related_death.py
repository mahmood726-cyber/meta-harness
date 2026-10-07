"""Plant: 'CV-related death' is cardiovascular death. TECOS's registered secondary outcome reads 'CV composite endpoint of
MACE which includes CV-related death, nonfatal MI, or nonfatal stroke'; the parser missed it, so D5 called TECOS's pooled
3-point MACE unregistered ('some concerns') and, scanning on, reached secondaries with no components -- the embedding
fallback, which CI cannot re-derive (PR #24 CI, publication gate L1). With the component recognised, D5 matches the
registered secondary deterministically and never calls a model."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import rob2  # noqa: E402

TECOS_SECONDARY = {"measure": "Percentage of Participants With First Confirmed CV Event of MACE (Intent to Treat Population)",
                   "title": "", "description": "CV composite endpoint of MACE which includes CV-related death, nonfatal MI, "
                                               "or nonfatal stroke."}


def test_cv_related_death_is_cardiovascular_death():
    assert rob2._component_set(TECOS_SECONDARY["description"]) == {"CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"}
    assert "CV_DEATH" in rob2._component_set("cardiovascular-related death")
    assert "CV_DEATH" not in rob2._component_set("non-cardiovascular death")


def test_d5_matches_the_registered_secondary_without_any_model():
    def no_model(a, b):
        raise AssertionError("D5 must not reach the embedding fallback here")
    primary = {"measure": "First Confirmed CV Event of MACE Plus", "title": "",
               "description": "CV death, nonfatal MI, nonfatal stroke, or hospitalization for unstable angina"}
    d = rob2.derive_d5([primary], "3-point major adverse cardiovascular events", no_model, [TECOS_SECONDARY])
    assert d["level"] == "low" and d["inputs"]["comparison"]["registered_type"] == "secondary"
