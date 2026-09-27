"""V1.0.1 engine positive controls (harness/positive_control.py): reproduce published meta-analyses from their own
forest-plot rows with harness/synth.pool."""
import copy
import os

import pytest

from harness import positive_control as pc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTROLS = {c["id"]: c for c in pc.load(ROOT)}


@pytest.mark.xfail(strict=True, raises=pc.PendingSource,
                   reason="WHO REACT Figure 2 rows not held (publisher disallows XML; JAMA/PMC pages not readable here). "
                          "When the rows are added as HELD this test runs -- and this marker must be removed (strict).")
def test_WHO_REACT_reproduced_by_our_engine():
    c = CONTROLS["who-react-2020-corticosteroids-28d-mortality"]
    got = pc.reproduce(c)
    assert pc.compare(c, got) == []


def test_a_pending_control_is_never_run_and_never_passes():
    c = CONTROLS["who-react-2020-corticosteroids-28d-mortality"]
    assert c["state"] == "PENDING_SOURCE" and c["rows"] is None and c["expected"]["PM_HK"] == [0.69616, 0.48171, 1.00607]
    with pytest.raises(pc.PendingSource, match="rows not held"):
        pc.reproduce(c)


def test_PLANT_the_comparison_fires_on_a_wrong_engine_result():
    c = {"id": "x", "state": "HELD", "measure": "OR", "tolerance": 5e-5,
         "rows": [{"label": "a", "events_int": 10, "n_int": 100, "events_ctl": 20, "n_ctl": 100},
                  {"label": "b", "events_int": 15, "n_int": 120, "events_ctl": 22, "n_ctl": 118},
                  {"label": "c", "events_int": 8, "n_int": 90, "events_ctl": 9, "n_ctl": 91}]}
    got = pc.reproduce(c)
    c["expected"] = {"CE": list(got["CE"]), "PM_HK": list(got["PM_HK"]), "I2": got["I2"]}
    assert pc.compare(c, got) == []                                     # its own numbers agree
    bad = copy.deepcopy(c)
    bad["expected"]["PM_HK"][2] += 1e-3                                  # a 0.001 error in one bound
    assert pc.compare(bad, got) and pc.compare(bad, got)[0][0] == "PM_HK"
