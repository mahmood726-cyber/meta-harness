"""A6 (lc lane, 11 Oct): the external-agreement adjudication notes printed trial values as literals ('We are k=1
(Vandermolen OR 8.25)') that the served reviews no longer hold (metformin is k=3, OR 2.07). A note judges ONE version
of the row: it carries no numbers, records the (k, estimate, scale) it was written for, and is withheld -- with a
re-adjudication flag -- when the served row has moved. The numbers a reader sees come from the served review."""
import importlib.util
import os
import re

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("external_agreement", os.path.join(_ROOT, "scripts", "external_agreement.py"))
EA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(EA)


def test_no_adjudication_note_carries_a_number():
    for slug, a in EA.ADJUDICATION.items():
        assert not re.search(r"\d", a["note"]), (slug, a["note"])


def test_every_note_records_the_row_it_judged():
    for slug, a in EA.ADJUDICATION.items():
        w = a["written_for"]
        assert {"k", "estimate", "scale"} <= set(w), slug


def test_PLANT_a_note_written_for_k1_is_withheld_when_the_served_pool_is_k3():
    EA.ADJUDICATION["__control_metformin"] = {"note": "Single trial against a pool.",
                                              "written_for": {"k": 1, "estimate": 8.25, "scale": "OR"}}
    try:
        r = EA._classify("__control_metformin", 2.0733, "OR", 2.64, "OR", "ovulation", k=3)
        assert r["adjudication"] == ""
        assert r["adjudication_status"] == "STALE_REQUIRES_READJUDICATION"
        assert "k=1" in r["adjudication_stale_detail"] and "k=3" in r["adjudication_stale_detail"]
        r = EA._classify("__control_metformin", 8.2491, "OR", 2.64, "OR", "ovulation", k=1)
        assert r["adjudication"] == "Single trial against a pool." and r["adjudication_status"] == "CURRENT"
    finally:
        EA.ADJUDICATION.pop("__control_metformin")


def test_the_served_rows_today_withhold_every_stale_note():
    """Built from the served reviews: no note survives on a row it was not written for."""
    d = EA.build()
    for row in d["rows"]:
        a = EA.ADJUDICATION.get(row["slug"])
        if a and row.get("adjudication_status") == "CURRENT":
            w = a["written_for"]
            assert row.get("k") == w["k"] and round(row["our_estimate"], 2) == round(w["estimate"], 2), row["slug"]
