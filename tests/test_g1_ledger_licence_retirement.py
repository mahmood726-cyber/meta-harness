"""Plants (V9-03): a comparator retired ONLY for its licence (R0 C1_OPEN_LICENCE) has no open text to quote, so the
denominator ledger takes the retirement's span from the recorded licence probe (outputs/k_gap/g1_binding/licences.json,
sha256 pinned): its verbatim entry for the retired PMID, which must say LOOKED_UP, not open, and no CC BY / CC0 licence."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_denominator_ledger as L  # noqa: E402


def test_PLANT_a_licence_retirement_cites_the_recorded_probe_verbatim():
    r = L.retired_comparator("doac-vte-recurrence", "29795629")
    assert r is not None and r["retired_pmid"] == "24963045" and r["reason_code"].startswith("R0:C1_OPEN_LICENCE")
    assert r["span"]["source"] == "outputs/k_gap/g1_binding/licences.json"
    assert '"24963045"' in r["span"]["text"] and '"open": false' in r["span"]["text"]
    raw = open(os.path.join(ROOT, r["span"]["source"]), encoding="utf-8").read()
    assert r["span"]["text"] in raw


def test_PLANT_an_open_licence_never_supports_a_licence_retirement(monkeypatch):
    real = L._licence_entry
    monkeypatch.setattr(L, "_licence_entry", lambda pmid: dict(real(pmid), open=True, license="cc by"))
    assert L.retired_comparator("doac-vte-recurrence", "29795629") is None
    monkeypatch.setattr(L, "_licence_entry", lambda pmid: None)
    assert L.retired_comparator("doac-vte-recurrence", "29795629") is None
