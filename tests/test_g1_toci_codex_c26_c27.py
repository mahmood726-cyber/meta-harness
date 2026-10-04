"""G1 tocilizumab: plants for the defects cross-vendor review NR-C26 / NR-C27 (Codex, read-only, 2026-10-04) found and
the lane verified by execution. Each test fails on the code before the fix.

  B1  binding: a title that DECLARES a non-randomised design never binds (PMID 33075713, 'a prospective open-label
      uncontrolled multicenter trial', cited CORIMUNO's NCT04331808 twice in its discussion and bound CORIMUNO-TOCI-1)
  B2  binding: a generic 'Clinical Trial' type binds by registration frequency only with the registration stated as its
      own or the trial named; an RCT-typed report still binds
  H1  sha256 gate: a lossy decode never makes different bytes pass (U+FFFD collision)
  D1  vnh dedupe: the same counts over two denominator kinds are two readings
  A1  AACT day-28 percentages: a shared registration's population groups are not mixed
  A2  AACT day-28 percentages type a timepoint only with both arms
  S1  SECONDARY_COUNT types the meta row only if it is that row's tuple
  T1  day 29 is another day for the sentence reader
Radius (measured): B1/B2 change 1 of 74 bindings (33075713 -> unbound; it carried no candidates); T1 changes 0 of 16
held texts' readings; A1/A2/S1 change no admitted row."""
from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

import g1_toci_cascade as c  # noqa: E402
import g1_toci_tracker as tr  # noqa: E402
import g1_toci_vnh_read as v  # noqa: E402
from g1 import tocilizumab as g  # noqa: E402

BODY = ("Discussion: the preliminary results of a randomized controlled trial (# NCT04331808 ) were announced; the "
        "interim results of the CORIMUNO-TOCI (# NCT04331808 ) trial were announced through a press release.")


def test_b1_a_non_randomised_title_never_binds():
    a = {"title": "Subcutaneous tocilizumab in adults with severe and critical COVID-19: A prospective open-label "
                  "uncontrolled multicenter trial.", "pub_types": ["Clinical Trial", "Journal Article"], "fulltext": BODY}
    labels, why = c.binding(a)
    assert labels == [] and "non-randomised" in why


def test_b2_generic_clinical_trial_type_needs_its_own_registration_or_name():
    a = {"title": "Tocilizumab in adults with severe COVID-19 pneumonia", "pub_types": ["Clinical Trial"], "fulltext": BODY}
    assert c.binding(a)[0] == []
    rct = dict(a, pub_types=["Randomized Controlled Trial"])
    assert c.binding(rct)[0] == ["CORIMUNO-TOCI-1"]


def test_h1_a_lossy_decode_never_passes_different_bytes(monkeypatch):
    recorded = hashlib.sha256(b"<body>\xef\xbf\xbd</body>").hexdigest()     # the text a 'replace' decode of 0xff gives
    monkeypatch.setattr(c, "get", lambda url, params=None: (200, b"<body>\xff</body>", url))
    monkeypatch.setattr(v.time, "sleep", lambda s: None)
    body, tried = v.fetch("PMC1", recorded)
    assert body is None and any("not valid UTF-8" in x for x in tried)


def test_d1_same_counts_over_two_denominator_kinds_are_two_readings(tmp_path, monkeypatch):
    cand = {"label": "COVIDSTORM", "extractor": "TABLE", "deaths_t": 1, "n_t": 57, "deaths_c": 0, "n_c": 29, "span": "x"}
    rec = {"1": {"state": "VERIFIED_NOT_HELD", "bound_labels": ["COVIDSTORM"], "pmcid": "PMC1", "body_sha256": "0" * 64,
                 "candidates": [dict(cand, denominator_kind=g.ANALYSED), dict(cand, denominator_kind=g.RANDOMISED)]}}
    p = tmp_path / "v.json"
    p.write_text(json.dumps(rec), encoding="utf-8")
    monkeypatch.setattr(g, "VNH_READS_FILE", str(p))
    assert sorted(x["denominator_kind"] for x in g.vnh_candidates("COVIDSTORM")) == [g.ANALYSED, g.RANDOMISED]


def _aact(tmp_path, groups):
    ex = {"outcomes": {"1": {"nct_id": "NCT04331808", "title": "Mortality at Day 28", "units": "percentage of participants",
                             "time_frame": "Day 28", "analysed": {grp: n for grp, _, n in groups},
                             "measurements": [{"group": grp, "classification": "Day 28", "value": val}
                                              for grp, val, _ in groups]}}}
    p = tmp_path / "aact.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    return str(p)


def test_a1_population_groups_of_a_shared_registration_are_not_mixed(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "AACT_FILE", _aact(tmp_path, [
        ("TOCILIZUMAB -- Severe COVID Population", "11", 63), ("Standard of Care -- Severe COVID Population", "12", 67),
        ("TOCILIZUMAB -- Critical COVID Population", "16", 49), ("Standard of Care -- Critical COVID Population", "23", 43)]))
    got = tr.aact_day28_percentages("CORIMUNO-TOCI-ICU")
    assert sorted((a, n) for a, _, n, _ in got) == [("c", 43), ("t", 49)]


def test_a2_one_arm_never_types_a_timepoint(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "AACT_FILE", _aact(tmp_path, [("TOCILIZUMAB -- Critical COVID Population", "16", 49)]))
    assert tr.aact_day28_percentages("CORIMUNO-TOCI-ICU") == []


def test_s1_secondary_count_types_only_its_own_tuple(monkeypatch):
    monkeypatch.setattr(tr, "VNH", os.path.join(ROOT, "no-such-file.json"))
    row = {"meta_pmid": "1", "label": "X 2020", "binding": "BOUND", "events_t": 7, "total_t": 63, "events_c": 8,
           "total_c": 67}
    t = {"label": "CORIMUNO-TOCI-1", "state": g.SECONDARY_COUNT, "meta2_rows": [row],
         "row": {"deaths_t": 9, "n_t": 63, "deaths_c": 8, "n_c": 67}}
    got, why = tr.secondary_single(t)
    assert got is None and "is not the meta row" in why
    ok, why2 = tr.secondary_single(dict(t, row={"deaths_t": 7, "n_t": 63, "deaths_c": 8, "n_c": 67}))
    assert ok and why2 is None


def test_t1_day_29_is_another_day_for_the_sentence_reader():
    s = ("Deaths up to day 29 (the day 28 analysis window): 10 of 100 patients in the tocilizumab group and 20 of 100 "
         "in the placebo group died.")
    assert g.text_candidates(s) == []
