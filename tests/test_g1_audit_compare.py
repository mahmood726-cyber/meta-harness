"""Plants (codex binding-v8-fe3ed2a7 g1#3-5, reproduced): the second-reader audit CONFIRMED a wrong control-arm SD, read
'100.0' as the count 1000, and let an HR confirm an RR."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from g1_audit_primary import compare  # noqa: E402

ARMS = {"arms": [{"label": "esketamine", "mean": "1", "sd": "2", "n": "100"},
                 {"label": "placebo", "mean": "0", "sd": "3", "n": "100"}]}


def test_a_wrong_control_sd_is_not_confirmed():
    assert compare(ARMS, {"mean_t": 1, "sd_t": 2, "n_t": 100, "mean_c": 0, "sd_c": 999, "n_c": 100}, ["esketamine"]) == ("DISAGREE", "ARMS")
    assert compare(ARMS, {"mean_t": 1, "sd_t": 2, "n_t": 100, "mean_c": 0, "sd_c": 3, "n_c": 100}, ["esketamine"]) == ("CONFIRMED", "ARMS")


def test_a_decimal_is_not_a_count():
    got = compare({"events_t": "1.0", "n_t": "100.0", "events_c": "2.0", "n_c": "100.0"},
                  {"events_t": 10, "n_t": 1000, "events_c": 20, "n_c": 1000}, [])
    assert got[0] != "CONFIRMED"
    assert compare({"events_t": "10", "n_t": "1,000", "events_c": "20", "n_c": "1000"},
                   {"events_t": 10, "n_t": 1000, "events_c": 20, "n_c": 1000}, []) == ("CONFIRMED", "COUNTS")


def test_a_different_measure_never_confirms():
    got = compare({"measure": "HR", "point": "0.8", "lower": "0.7", "upper": "0.9"},
                  {"measure": "RR", "effect": "0.8", "lower": "0.7", "upper": "0.9"}, [])
    assert got[0] == "NOT_COMPARABLE"
    assert compare({"measure": "risk ratio", "point": "0.8", "lower": "0.7", "upper": "0.9"},
                   {"measure": "RR", "effect": "0.8", "lower": "0.7", "upper": "0.9"}, [])[0] == "CONFIRMED"
