"""Plants (8 Oct, forest lane): the typed (regex) table reader parses exactly one block's events/N, refuses a cell it
cannot parse rather than guessing, and its rows meet the forest reader's unchanged pooled-reconstruction gate."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_typed_table as tt  # noqa: E402

SPEC = {"table_id": "t1", "block": "VTE Studies", "caption_has": "Primary outcomes", "cols": {"label": 0, "t": 1, "c": 2}}


def _xml(rows):
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table-wrap id="t1"><caption><p>Primary outcomes</p></caption><table>{tr}</table></table-wrap>'


def test_only_the_named_block_is_read():
    x = _xml([["AF Studies", "", ""], ["RE-LY", "182/6015", "199/6022"], ["VTE Studies", "", ""],
              ["RE-COVER", "30/1274", "27/1265"], ["AMPLIFY", "59/2,609", "71/2635"]])
    rows, probs = tt.table_rows(x, SPEC)
    assert probs == [] and [r["label"] for r in rows] == ["RE-COVER", "AMPLIFY"]
    assert rows[1]["n_t"] == 2609 and rows[0]["events_c"] == 27


def test_an_unparsable_or_impossible_count_is_refused_never_guessed():
    x = _xml([["VTE Studies", "", ""], ["A", "30 of 1274", "27/1265"], ["B", "300/200", "1/10"]])
    rows, probs = tt.table_rows(x, SPEC)
    assert rows == [] and probs == ["COUNT_CELL_NOT_PARSED:A", "EVENTS_EXCEED_N:B"]


def test_the_doac_table_meets_the_unchanged_reconstruction_gate_and_records_its_margin():
    # 29795629 states random effects; tau2 = 0, so DL/PM/REML give 0.881 (0.749-1.036) vs printed 0.88 (0.75-1.03).
    # The upper bound is inside the gate's allowance (printed rounding + half-unit row-rounding extra: 0.0058 <= 0.010)
    # but outside printed rounding alone; the margin is recorded so a reviewer sees it (M-H fixed gives 1.0350)
    r = tt.judge("doac-vte-recurrence")
    assert len(r["proposed_rows"]) == 5 and r["state"] == "ACCEPTED"
    assert r["acceptance"]["methods_reproducing"] == ["DL", "PM", "REML"]
    assert r["margin"]["upper_outside_printed_rounding"] is True
