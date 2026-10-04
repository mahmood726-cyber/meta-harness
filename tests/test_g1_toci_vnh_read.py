"""G1 tocilizumab: a primary full text that is fetched but NOT held (its licence is not open) is bound and read from its
BODY, not its abstract (scripts/g1_toci_vnh_read.py -> g1/data/vnh_reads.json -> g1.tocilizumab.vnh_candidates).

COVIDSTORM's report (PMID 35259529, PMC8897958, CMI 2022) names NCT04577534 only in its body; read from its abstract the
cascade recorded it 'UNBOUND: names no registration' and the trial was listed as structurally unreachable. Its Table 3
states 'Death at day 28, n (%) 1 (1.8) 0 (0)' under 'Tocilizumab group ( n = 57) Standard-of-care group ( n = 29)'.
REACT's row is 0/26 vs 0/13: a verified PRIMARY row that DISAGREES, with the side named from the report's own span.
Radius: the 20 not-held papers (all 20 sha256s matched the cascade's records); new readings: COVIDSTORM (day 28),
COVACTA's NEJM table (58/294 vs 28/144, = its established row), BACC-Bay (safety table, = its known safety count)."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

from g1 import tocilizumab as g  # noqa: E402

READS = os.path.join(ROOT, "g1", "data", "vnh_reads.json")
TRACK = os.path.join(ROOT, "outputs", "k_gap", "g1", "tocilizumab-covid19-mortality.json")


def _reads():
    return json.load(open(READS, encoding="utf-8"))


def test_v1_covidstorm_is_bound_from_its_body_not_its_abstract():
    import g1_toci_cascade as c
    a = json.load(open(os.path.join(ROOT, "g1", "data", "acquired", "35259529.json"), encoding="utf-8"))
    assert c.binding(a)[0] == []                       # the abstract alone names no registration
    r = _reads()["35259529"]
    assert r["state"] == "VERIFIED_NOT_HELD" and r["bound_labels"] == ["COVIDSTORM"]
    assert r["body_sha256"] == a["fulltext_sha256"]    # read only the bytes the cascade recorded


def test_v2_the_recorded_span_reproduces_the_counts_through_the_lane_reader():
    x = next(x for x in _reads()["35259529"]["candidates"] if x["label"] == "COVIDSTORM")
    head, *_, row = x["span"].split(" ... ")
    # the committed span alone, through the same extractor, gives the same four numbers (no hand-typed counts)
    got = g.table_candidates(x["span"].replace(" ... ", " "))
    assert [(c["deaths_t"], c["n_t"], c["deaths_c"], c["n_c"]) for c in got] == [(1, 57, 0, 29)]
    assert row.startswith("Death at day 28")


def test_v3_covidstorm_reading_enters_assess_as_a_primary_text():
    c = g.vnh_candidates("COVIDSTORM")
    assert [(x["deaths_t"], x["n_t"], x["deaths_c"], x["n_c"]) for x in c] == [(1, 57, 0, 29)]
    assert c[0]["source"].startswith("TEXT PMID 35259529 (VERIFIED_NOT_HELD PMC8897958 sha256 35eaf4ca1bfc")


def test_v4_an_unverified_or_foreign_record_is_never_read(tmp_path, monkeypatch):
    fake = {"1": {"state": "SHA_MISMATCH (nothing read)", "bound_labels": ["COVIDSTORM"], "pmcid": "PMC1",
                  "body_sha256": "0" * 64, "candidates": [{"label": "COVIDSTORM", "extractor": "TABLE", "deaths_t": 5,
                                                           "n_t": 50, "deaths_c": 5, "n_c": 50,
                                                           "denominator_kind": "UNSTATED", "span": "x"}]},
            "2": {"state": "VERIFIED_NOT_HELD", "bound_labels": ["TOCOVID"], "pmcid": "PMC2", "body_sha256": "1" * 64,
                  "candidates": [{"label": "TOCOVID", "extractor": "TABLE", "deaths_t": 5, "n_t": 50, "deaths_c": 5,
                                  "n_c": 50, "denominator_kind": "UNSTATED", "span": "x"}]}}
    p = tmp_path / "vnh.json"
    p.write_text(json.dumps(fake), encoding="utf-8")
    monkeypatch.setattr(g, "VNH_READS_FILE", str(p))
    assert g.vnh_candidates("COVIDSTORM") == []        # sha mismatch: nothing read
    assert g.vnh_candidates("COVINTOC") == []          # bound to another trial
    assert len(g.vnh_candidates("TOCOVID")) == 1


def test_v5_covidstorm_is_a_verified_primary_that_disagrees_with_its_side_named():
    o = json.load(open(TRACK, encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"] == "COVIDSTORM")
    assert x["route"] == "PRIMARY" and x["g1_countable"]
    assert x["agreement_with_comparator_row"] == "DISAGREE"
    assert x["disagreement_side"].startswith("SECONDARY_WRONG") and "Death at day 28, n (%) 1 (1.8) 0 (0)" in x["disagreement_side"]
    # every per-trial disagreement carries its side (g1_tracker DIVERGENCES_NAMED)
    assert all(t.get("disagreement_side") for t in o["trials"] if str(t["agreement_with_comparator_row"]).startswith("DISAGREE"))
    assert not any(t.get("disagreement_side") for t in o["trials"] if t["agreement_with_comparator_row"] == "AGREE")


def test_v6_a_safety_table_read_from_a_body_stays_safety():
    c = g.vnh_candidates("BACC-Bay")
    assert c and all(x["source"].endswith("(safety-population table)") and x["denominator_kind"] == g.SAFETY for x in c)
