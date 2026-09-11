"""Second independent extractor: _cross_source corroborates an abstract-pooled trial against CT.gov
structured results, with an adjudication verdict and no replacement of the pooled number."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.pipeline import _cross_source, _rr_cs  # noqa: E402

SPEC = {"keywords": ["mortality", "death"]}
INTERV = ["drug"]
COMP = ["placebo", "control"]


def _om(ai, n1, ci, n2, title="30-day mortality"):
    return {"title": title, "type": "PRIMARY", "paramType": "COUNT_OF_PARTICIPANTS",
            "groups": [{"id": "g1", "title": "Drug"}, {"id": "g2", "title": "Placebo control"}],
            "classes": [{"categories": [{"measurements": [
                {"groupId": "g1", "value": str(ai)}, {"groupId": "g2", "value": str(ci)}]}]}],
            "denoms": [{"counts": [{"groupId": "g1", "value": str(n1)}, {"groupId": "g2", "value": str(n2)}]}]}


def test_agreeing_counts_are_corroborated():
    ex = {"ai": 100, "n1i": 1000, "ci": 120, "n2i": 1000}
    cs = _cross_source(ex, "NCT1", {"NCT1": [_om(101, 1000, 119, 1000)]}, SPEC, INTERV, COMP)
    assert cs and cs["agree"] is True
    assert "corroborated" in cs["note"]
    assert cs["ctgov_rr"] and cs["abstract_rr"]


def test_direction_flip_is_flagged_discrepancy():
    ex = {"ai": 50, "n1i": 1000, "ci": 150, "n2i": 1000}  # abstract RR ~0.33 (protective)
    cs = _cross_source(ex, "NCT1", {"NCT1": [_om(150, 1000, 50, 1000)]}, SPEC, INTERV, COMP)  # ctgov RR ~3 (harmful)
    assert cs and cs["agree"] is False
    assert "DISCREPANCY" in cs["note"]


def test_no_ctgov_returns_none():
    assert _cross_source({"ai": 1, "n1i": 2, "ci": 1, "n2i": 2}, "NCT1", {}, SPEC, INTERV, COMP) is None


def test_effect_only_gets_corroboration_note_not_verdict():
    ex = {"effect": 0.85}  # abstract gave an HR, no counts
    cs = _cross_source(ex, "NCT1", {"NCT1": [_om(100, 1000, 120, 1000)]}, SPEC, INTERV, COMP)
    assert cs and cs["agree"] is None
    assert cs["ctgov_rr"] is not None


def test_rr_cs_guards():
    assert _rr_cs(0, 100, 10, 100) is None  # zero event cell
    assert _rr_cs(10, 0, 10, 100) is None   # zero denom
    assert abs(_rr_cs(100, 1000, 200, 1000) - 0.5) < 1e-9
