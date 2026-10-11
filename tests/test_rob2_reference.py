"""Plants for the calibration reference transcription (scripts/rob2_reference.py): a malformed reading is never paired,
and figure labels bind to trials only through the comparator's own reference list."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_reference as rr  # noqa: E402

COLS = ["D1", "D2", "D3", "D4", "D5", "Overall"]


def _r(rows):
    return {"legible": True, "per_study": True, "tool": "RoB 2", "legend": "", "columns": COLS, "rows": rows, "notes": ""}


def test_PLANT_a_reading_without_row_labels_is_malformed_not_adjudicated():
    # agy, 10 Oct: every row came back with no 'label'; nothing paired and the 'reference' became one codex reading
    bad = _r([{"cells": ["low"] * 6}, {"label": None, "cells": ["low"] * 6}])
    assert rr.shape_problems(bad) == ["ROW_0_NO_LABEL", "ROW_1_NO_LABEL"]
    assert rr.cells(bad) == ({}, {})
    short = _r([{"label": "Anker 2009", "cells": ["low"] * 5}])
    assert rr.shape_problems(short) == ["ROW_0_CELLS_5_NE_COLUMNS_6"]


def test_PLANT_D8_a_figure_of_a_non_cc_comparator_is_never_read(tmp_path, monkeypatch):
    # the metformin Cochrane review (31845767): no CC licence in any held copy
    assert rr.comparator_open("31845767") is False
    assert rr.figure("metformin-pcos-ovulation", run=False) == (None, "D8_COMPARATOR_NOT_CC")
    assert rr.comparator_open("34385227") is True                    # probiotics comparator: CC BY in its JATS


def test_two_wellformed_readings_pair_by_label():
    a = _r([{"label": "Anker et al. 2009", "cells": ["low", "low", "low", "some concerns", "low", "low"]}])
    b = _r([{"label": "Anker et al 2009", "cells": ["low", "low", "low", "some concerns", "low", "high"]}])
    agreed, disputed, _ = rr.compare(a, b)
    assert len(agreed) == 5 and list(disputed) == [("ankeretal2009", 5)]


def test_PLANT_labels_bind_only_through_one_matching_reference():
    refs = [("Anker", "2009", "19920054", "Anker SD ... 2009"), ("Ponikowski", "2015", "25176939", "Ponikowski P ... 2015"),
            ("Ponikowski", "2020", "33197395", "Ponikowski P ... 2020")]
    assert rr.bind_label("Anker et al. 2009", refs)[0] == "19920054"
    assert rr.bind_label("Ponikowski et al. 2020", refs)[0] == "33197395"
    assert rr.bind_label("van Veldhuisen et al. 2017", refs)[0] is None          # no matching reference: unbound
    twice = refs + [("Anker", "2009", "11111111", "another Anker 2009")]
    assert rr.bind_label("Anker 2009", twice) == (None, "REFERENCE_MATCHES_2")    # ambiguous: unbound, never a guess
