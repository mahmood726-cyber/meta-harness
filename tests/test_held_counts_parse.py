"""held_rows.ascertained_counts never does arithmetic on unparsed counts (pass 19). Before it, a typed arm whose events/n came through as
text ('9 (0.3)', '3494') raised TypeError inside the producer and stopped two whole reviews from regenerating (balanced-crystalloids,
esketamine, 2026-09-29). A count that is not a plain non-negative integer is NOT ascertainable -- reported, never computed with."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import held_rows  # noqa: E402


def test_PLANT_text_counts_do_not_crash_and_are_not_ascertainable():
    got = held_rows.ascertained_counts({"arms": [{"arm": "A", "events": "9 (0.3)", "n": "3494", "n_group": "3494"},
                                                 {"arm": "B", "events": 12, "n": 100, "n_group": 110}]})
    a, b = got["arms"]
    assert a["n_ascertained"] is None and a["non_events"] is None and a["denominator_basis"].startswith("NOT_ASCERTAINABLE")
    assert (b["n_ascertained"], b["non_events"], b["missing"]) == (100, 88, 10)


def test_digit_strings_with_thousands_separators_are_counts():
    got = held_rows.ascertained_counts({"arms": [{"arm": "A", "events": "12", "n": "1,234", "n_group": "1,300"},
                                                 {"arm": "B", "events": "3", "n": "1,200", "n_group": "1,300"}]})
    assert [(x["non_events"], x["missing"]) for x in got["arms"]] == [(1222, 66), (1197, 100)]


def test_events_above_the_denominator_are_not_ascertainable():
    got = held_rows.ascertained_counts({"arms": [{"arm": "A", "events": 120, "n": 100}, {"arm": "B", "events": 5, "n": 100}]})
    assert got["arms"][0]["denominator_basis"].startswith("NOT_ASCERTAINABLE") and got["arms"][1]["non_events"] == 95
