"""R6 P2 dpp4 hHF bindings (scripts/g1_r6_dpp4_hf.py): a binding is staged only when its span is verbatim in the
trial's own abstract (which carries the trial's NCT), every value is printed in the span, and BOTH recorded readers quote
that same clause with the same numbers. EXAMINE's 'first event' count is never staged."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_r6_dpp4_hf as H  # noqa: E402

T = H.TARGETS[1]                                                # CARMELINA
AB = {"abstract": "Background. " + T["span"] + ", the composite of cardiovascular death/hHF (HR, 0.94; 95% CI, 0.82-1.08).",
      "ncts": ["NCT01897532"]}


def test_the_carmelina_first_event_clause_verifies():
    assert H.verify(T, AB) is None


def test_PLANT_a_binding_whose_span_or_value_is_not_in_the_trials_own_abstract_is_refused():
    assert H.verify(T, dict(AB, ncts=["NCT00000000"])) == "ABSTRACT_DOES_NOT_CARRY_THE_TRIAL_NCT"
    assert H.verify(T, dict(AB, abstract=AB["abstract"].replace("0.74-1.08", "0.75-1.08"))) == "SPAN_NOT_VERBATIM"
    bad = dict(T, value=dict(T["value"], upper=1.09))
    assert H.verify(bad, AB).startswith("VALUE_NOT_IN_SPAN")
    assert H.verify(T, None) == "ABSTRACT_NOT_FETCHED"


def test_PLANT_a_reader_quoting_another_clause_never_confirms():
    other = {"state": "FOUND", "quote": "the composite of cardiovascular death/hHF (HR, 0.94; 95% CI, 0.82-1.08)",
             "hr": 0.94, "lower": 0.82, "upper": 1.08}
    assert H.gate(other, AB["abstract"], T) == "GATED_OTHER_CLAUSE"
    ok = {"state": "FOUND", "quote": T["span"], "hr": 0.90, "lower": 0.74, "upper": 1.08}
    assert H.gate(ok, AB["abstract"], T) == "GATED_AGREES"


def test_PLANT_examine_is_never_staged():
    ex = [t for t in H.TARGETS if t["label"] == "EXAMINE"][0]
    assert ex["state"] == "REFUSED_DEFINITION"
