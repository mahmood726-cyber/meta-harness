"""Signed comparator findings (registry/g1_signed_comparator_findings.json; g1_tracker.signed_comparator_findings).

D14 (V10-04Q, signed): CONFIRM-HF's incidence numerator is PATIENTS, 10 v 25 of 150/151; the comparator's 32 is the
EVENT count (Table 2: 'Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)'). The finding is named in the
tracker only when it verifies at build (held document by sha256, span verbatim, the comparator's numerators and ours in
their declared cells, the trial's comparator row carrying the comparator's numerators), and only when it is SIGNED. An
unsigned entry is listed as proposed and never sets a side. Fixtures are synthetic."""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

DOC = ("<caption>Table 2 Hospitalizations and deaths (full-analysis set)</caption><th>FCM ( n = 150)</th>"
       "<th>Placebo ( n = 151)</th><td>Hospitalizations due to worsening HF</td><td>10</td><td>10 (7.6)</td>"
       "<td>32</td><td>25 (19.4)</td>")
ROW = "Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)"


def setup(tmp_path, signed=True, **kw):
    (tmp_path / "doc.txt").write_text(DOC, encoding="utf-8")
    e = {"slug": "t", "pmid": "1", "label": "CONFIRM-HF", "state": "SIGNED" if signed else "PROPOSED",
         "decision": "D14 (V10-04Q)", "finding": "COMPARATOR_COUNTS_ARE_EVENTS",
         "doc": {"path": "doc.txt", "format": "xml",
                 "text_sha256": hashlib.sha256(DOC.encode("utf-8")).hexdigest()},
         "row_span": ROW, "cells": {"comparator": {"events_t": 0, "events_c": 3}, "ours": {"events_t": 1, "events_c": 4}},
         "comparator_counts": {"events_t": 10, "events_c": 32}, "our_counts": {"events_t": 10, "events_c": 25}}
    e.update(kw)
    (tmp_path / "reg.json").write_text(json.dumps({"findings": [e]}), encoding="utf-8")
    return str(tmp_path / "reg.json")


def trial(agree="DISAGREE"):
    return {"label": "CONFIRM-HF [2]", "family": "PMID 1", "agreement_with_comparator_row": agree,
            "comparator_row": {"events_t": 10, "n_t": 150, "events_c": 32, "n_c": 151, "measure": "OR"}}


def test_PLANT_a_signed_verified_finding_names_the_comparator_side(tmp_path):
    x = trial()
    gt.signed_comparator_findings([x], "t", reg=setup(tmp_path), root=str(tmp_path))
    assert str(x.get("disagreement_side")).startswith("SECONDARY_WRONG (D14 (V10-04Q): COMPARATOR_COUNTS_ARE_EVENTS")
    assert x["comparator_finding"]["state"] == "SIGNED"


def test_PLANT_an_unsigned_finding_is_listed_never_applied(tmp_path):
    x = trial()
    gt.signed_comparator_findings([x], "t", reg=setup(tmp_path, signed=False), root=str(tmp_path))
    assert x.get("disagreement_side") is None and x["comparator_finding_proposed"]["finding"] == "COMPARATOR_COUNTS_ARE_EVENTS"


def test_PLANT_a_finding_that_does_not_verify_is_refused_by_name(tmp_path):
    for kw in ({"row_span": ROW.replace("32", "33")},
               {"comparator_counts": {"events_t": 10, "events_c": 31}},
               {"doc": {"path": "doc.txt", "format": "xml", "text_sha256": "0" * 64}}):
        x = trial()
        gt.signed_comparator_findings([x], "t", reg=setup(tmp_path, **kw), root=str(tmp_path))
        assert x.get("disagreement_side") is None and x["comparator_finding_refused"], kw


def test_PLANT_the_comparator_row_must_carry_the_numerators_named(tmp_path):
    x = trial()
    x["comparator_row"]["events_c"] = 30
    gt.signed_comparator_findings([x], "t", reg=setup(tmp_path), root=str(tmp_path))
    assert x.get("disagreement_side") is None and "COMPARATOR_ROW" in x["comparator_finding_refused"]


def test_a_side_already_named_is_never_overwritten(tmp_path):
    x = dict(trial(), disagreement_side="COMPARATOR_ARMS_SWAPPED (...)")
    gt.signed_comparator_findings([x], "t", reg=setup(tmp_path), root=str(tmp_path))
    assert x["disagreement_side"] == "COMPARATOR_ARMS_SWAPPED (...)"
