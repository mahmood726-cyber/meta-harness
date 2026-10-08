"""D12 K5 -- a held DOCUMENT's table row (8 Oct, binding lane, final-5). K2 reads only the held abstract, and two staged
count sets are printed only in a table: CONFIRM-HF Table 2 (CC BY, held: patients with a worsening-HF hospitalisation
'10 (7.6)' v '25 (19.4)' of n = 150 / 151) and RECOVERY's supplementary Table S2 (NEJM COVID licence, NOT
redistributable: '95/324 (29.3%)' v '283/683 (41.4%)', the ventilated subgroup). A K5 binding is used only when:
  - the document is held and its text hashes to the binding's sha256 (absent or changed -> unused; fail closed);
  - caption, header and row are each verbatim in it, in that order, within one table's reach;
  - the declared outcome span (the row label, or the caption for a subgroup row) passes the topic's endpoint gate;
  - the arm order is read from the header's own arm terms, and each declared cell holds its count (an 'e/N' cell must
    carry its own N; a bare count takes the header's '(n = N)' for its arm);
  - an INDEPENDENT second reader states the same four counts: two recorded readers' gated answers, or a second
    extraction of the same document (a different text-extraction mode) holding the same cells.
Fixtures are synthetic: they never point at a live corpus."""
import base64
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_d12 as D  # noqa: E402

TOPIC = {"intervention_terms": ["ferric carboxymaltose", "FCM"], "comparator_terms": ["placebo"],
         "primary_outcome": {"name": "Heart-failure hospitalization", "keywords": ["hospitalizations due to worsening HF"]}}
DOC = ("<p>Results</p><table-wrap><caption>Table 2 Hospitalizations and deaths (full-analysis set)</caption>"
       "<th>End-point or event</th><th>FCM ( n = 150)</th><th>Placebo ( n = 151)</th>"
       "<td>Death</td><td>12</td><td>12 (8.9)</td><td>14</td><td>14 (9.9)</td>"
       "<td>Hospitalizations due to worsening HF</td><td>10</td><td>10 (7.6)</td><td>32</td><td>25 (19.4)</td>"
       "<td>0.39 (0.19-0.82)</td></table-wrap>")
SUB = ("Table S2: effect of allocation to dexamethasone on 28-day mortality, by respiratory support\n"
       "Dexamethasone\n(n=2104)\nUsual care\n(n=4321) RR (95% CI)\nOxygen only 298/1279\n(23.3%)\n682/2604\n(26.2%)\n"
       "Invasive mechanical ventilation 95/324\n(29.3%)\n283/683\n(41.4%)\n0.64 (0.51-0.81)\n")
SUB_T = {"intervention_terms": ["dexamethasone"], "comparator_terms": ["usual care"],
         "primary_outcome": {"name": "28-day all-cause mortality", "keywords": ["28-day mortality"]}}


def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "ROOT", str(tmp_path))
    (tmp_path / "topics").mkdir()
    (tmp_path / "topics" / "iv.json").write_text(json.dumps(TOPIC), encoding="utf-8")
    (tmp_path / "topics" / "co.json").write_text(json.dumps(SUB_T), encoding="utf-8")
    (tmp_path / "doc.txt").write_text(DOC, encoding="utf-8")
    (tmp_path / "sub_raw.txt").write_text(SUB, encoding="utf-8")
    (tmp_path / "sub_layout.txt").write_text(SUB.replace("\n", "   "), encoding="utf-8")
    rec = tmp_path / "rec"
    rec.mkdir()
    for rid, vals in (("mc-a", (10, 150, 25, 151)), ("mc-b", (10, 150, 25, 151))):
        record(rec, rid, vals)


QUOTE = "FCM ( n = 150) Placebo ( n = 151)\nHospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)"


def record(rec, rid, vals, quote=QUOTE, pmid="1", state="RAN_OK"):
    """A recorded reader call as the record format stores it: the response is READ from its bytes, never a label."""
    resp = dict(zip(D._VALUE_KEYS, vals), state="FOUND", quote=quote)
    (rec / f"{rid}.json").write_text(json.dumps({
        "record_id": rid, "state": state, "input_digests": [{"ref": f"PMID {pmid} PMC OA full text (CC BY)"}],
        "response": {"b64": base64.b64encode(json.dumps(resp).encode("utf-8")).decode("ascii")}}), encoding="utf-8")


def sha(p):
    return hashlib.sha256(open(p, encoding="utf-8").read().encode("utf-8")).hexdigest()


def k5(tmp_path, **kw):
    b = {"rule": "K5", "tuple_kind": "COUNTS", "own_tuple": True, "slug": "iv", "pmid": "1", "label": "CONFIRM-HF",
         "values": {"events_t": 10, "n_t": 150, "events_c": 25, "n_c": 151},
         "doc": {"path": "doc.txt", "format": "xml", "text_sha256": sha(tmp_path / "doc.txt")},
         "caption_span": "Table 2 Hospitalizations and deaths (full-analysis set)",
         "header_span": "FCM ( n = 150) Placebo ( n = 151)",
         "row_span": "Hospitalizations due to worsening HF 10 10 (7.6) 32 25 (19.4)",
         "outcome_from": "row", "cells": {"events_t": 1, "events_c": 4},
         "second_reader": {"kind": "RECORDED_READERS", "dir": "rec", "record_ids": ["mc-a", "mc-b"]}}
    b.update(kw)
    return b


def ep(slug):
    t = TOPIC if slug == "iv" else SUB_T
    kws = [k.lower() for k in t["primary_outcome"]["keywords"]]
    return lambda title: any(k in title.lower() for k in kws) and "death" not in title.lower()


def test_k5_a_held_table_row_verifies(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    ok, why = D.verify(k5(tmp_path), None, ep("iv"))
    assert ok, why


def test_PLANT_k5_absent_or_changed_document_is_unused(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    assert D.verify(k5(tmp_path, doc={"path": "nope.txt", "text_sha256": "0" * 64}), None, ep("iv"))[1] \
        == "K5_DOCUMENT_NOT_HELD"
    assert D.verify(k5(tmp_path, doc={"path": "doc.txt", "format": "xml", "text_sha256": "0" * 64}), None, ep("iv"))[1] \
        == "K5_DOCUMENT_CHANGED"


def test_PLANT_k5_the_events_column_is_not_the_patients_column(tmp_path, monkeypatch):
    # cells 0 and 2 are the TOTAL EVENTS (10 v 32): a binding that declares them as patients' counts with 32 is refused
    setup(tmp_path, monkeypatch)
    b = k5(tmp_path, values={"events_t": 10, "n_t": 150, "events_c": 32, "n_c": 151})
    assert D.verify(b, None, ep("iv"))[1].startswith("K5_CELL_IS_NOT_THE_COUNT")


def test_PLANT_k5_spans_must_be_verbatim_and_in_table_order(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    assert D.verify(k5(tmp_path, row_span="Hospitalizations due to worsening HF 10 10 (7.6) 32 26 (19.4)"), None,
                    ep("iv"))[1] == "K5_SPAN_NOT_VERBATIM:row_span"
    # a 'header' that sits AFTER the row it is said to head
    assert D.verify(k5(tmp_path, header_span="25 (19.4) 0.39 (0.19-0.82)"), None, ep("iv"))[1] \
        == "K5_SPANS_NOT_IN_TABLE_ORDER"


def test_PLANT_k5_the_outcome_span_passes_the_endpoint_gate(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    assert D.verify(k5(tmp_path, outcome_from="caption"), None, ep("iv"))[1] == "K5_OUTCOME_NOT_OUR_ENDPOINT"
    assert D.verify(k5(tmp_path), None, None)[1] == "K5_ENDPOINT_NOT_CHECKABLE"


def test_PLANT_k5_ns_come_from_the_header_in_its_arm_order(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    b = k5(tmp_path, values={"events_t": 10, "n_t": 151, "events_c": 25, "n_c": 150})
    assert D.verify(b, None, ep("iv"))[1] == "K5_NS_NOT_THE_HEADER_NS_IN_ARM_ORDER"


def test_PLANT_k5_needs_an_independent_second_reader_stating_the_same_counts(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    assert D.verify(k5(tmp_path, second_reader=None), None, ep("iv"))[1] == "K5_NO_SECOND_READER"
    record(tmp_path / "rec", "mc-b", (10, 150, 32, 151))
    assert D.verify(k5(tmp_path), None, ep("iv"))[1].startswith("K5_SECOND_READER_DIFFERS")
    # a reader of ANOTHER paper, a failed call, or a quote not in the held document confirms nothing
    record(tmp_path / "rec", "mc-b", (10, 150, 25, 151), pmid="9")
    assert D.verify(k5(tmp_path), None, ep("iv"))[1].startswith("K5_SECOND_READER_NOT_ABOUT_THIS_PAPER")
    record(tmp_path / "rec", "mc-b", (10, 150, 25, 151), state="RAN_ERROR")
    assert D.verify(k5(tmp_path), None, ep("iv"))[1].startswith("K5_SECOND_READER_DIFFERS")
    record(tmp_path / "rec", "mc-b", (10, 150, 25, 151), quote="Hospitalizations due to worsening HF 10 of 150 25 of 151")
    assert D.verify(k5(tmp_path), None, ep("iv"))[1].startswith("K5_SECOND_READER_QUOTE_NOT_IN_DOCUMENT")


def test_k5_a_subgroup_row_with_its_own_ns_and_a_second_extraction(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    b = {"rule": "K5", "tuple_kind": "COUNTS", "own_tuple": True, "slug": "co", "pmid": "2", "label": "RECOVERY",
         "values": {"events_t": 95, "n_t": 324, "events_c": 283, "n_c": 683},
         "doc": {"path": "sub_raw.txt", "format": "text", "text_sha256": sha(tmp_path / "sub_raw.txt")},
         "caption_span": "Table S2: effect of allocation to dexamethasone on 28-day mortality, by respiratory support",
         "header_span": "Dexamethasone (n=2104) Usual care (n=4321)",
         "row_span": "Invasive mechanical ventilation 95/324 (29.3%) 283/683 (41.4%)",
         "outcome_from": "caption", "cells": {"events_t": 0, "events_c": 2},
         "second_reader": {"kind": "SECOND_EXTRACTION",
                           "doc": {"path": "sub_layout.txt", "format": "text",
                                   "text_sha256": sha(tmp_path / "sub_layout.txt")},
                           "row_span": "Invasive mechanical ventilation 95/324 (29.3%) 283/683 (41.4%)"}}
    ok, why = D.verify(b, None, ep("co"))
    assert ok, why
    # an e/N cell carries its OWN denominator: the header's whole-trial Ns are never used for it
    bad = dict(b, values={"events_t": 95, "n_t": 2104, "events_c": 283, "n_c": 4321})
    assert D.verify(bad, None, ep("co"))[1].startswith("K5_CELL_IS_NOT_THE_COUNT")
    # the second extraction is a DIFFERENT file: the same file twice is not a second reader
    same = dict(b, second_reader=dict(b["second_reader"], doc=b["doc"]))
    assert D.verify(same, None, ep("co"))[1] == "K5_SECOND_EXTRACTION_IS_THE_SAME_DOCUMENT"


def test_PLANT_k5_a_plain_text_document_is_never_tag_stripped(tmp_path, monkeypatch):
    # RECOVERY's appendix text holds '(<0.5%)' ... 'p >0.05': stripping '<...>' as if it were markup deleted everything
    # between them, Table S2's row included (8 Oct). A 'text' document is matched as printed; only 'xml' is stripped.
    setup(tmp_path, monkeypatch)
    pre = "Treatments given Dexamethasone 2 (<0.5%) 4 (<0.5%)\nP-values shown to 2 dp if >0.05\n"
    (tmp_path / "sub_raw.txt").write_text(pre.replace("2 dp", "2 dp") + SUB.replace("RR (95% CI)", "RR (95% CI) (<0.5%)")
                                          + "shown if >0.05\n", encoding="utf-8")
    (tmp_path / "sub_layout.txt").write_text(SUB.replace("\n", "   "), encoding="utf-8")
    b = {"rule": "K5", "tuple_kind": "COUNTS", "own_tuple": True, "slug": "co", "pmid": "2", "label": "RECOVERY",
         "values": {"events_t": 95, "n_t": 324, "events_c": 283, "n_c": 683},
         "doc": {"path": "sub_raw.txt", "format": "text", "text_sha256": sha(tmp_path / "sub_raw.txt")},
         "caption_span": "Table S2: effect of allocation to dexamethasone on 28-day mortality, by respiratory support",
         "header_span": "Dexamethasone (n=2104) Usual care (n=4321)",
         "row_span": "Invasive mechanical ventilation 95/324 (29.3%) 283/683 (41.4%)",
         "outcome_from": "caption", "cells": {"events_t": 0, "events_c": 2},
         "second_reader": {"kind": "SECOND_EXTRACTION",
                           "doc": {"path": "sub_layout.txt", "format": "text",
                                   "text_sha256": sha(tmp_path / "sub_layout.txt")},
                           "row_span": "Invasive mechanical ventilation 95/324 (29.3%) 283/683 (41.4%)"}}
    ok, why = D.verify(b, None, ep("co"))
    assert ok, why
    # an undeclared format is refused, never guessed
    nb = dict(b, doc={k: v for k, v in b["doc"].items() if k != "format"})
    assert D.verify(nb, None, ep("co"))[1] == "K5_DOCUMENT_FORMAT_UNDECLARED"


def test_PLANT_k5_a_caption_repeated_in_a_table_of_contents_still_finds_its_table(tmp_path, monkeypatch):
    # RECOVERY's appendix lists 'Table S2: ...' in its contents pages, thousands of characters before the table: the
    # FIRST occurrence is not the table's own caption (8 Oct)
    setup(tmp_path, monkeypatch)
    toc = "Contents\nTable S2: effect of allocation to dexamethasone on 28-day mortality, by respiratory support .... 32\n"
    (tmp_path / "sub_raw.txt").write_text(toc + "filler text. " * 900 + SUB, encoding="utf-8")
    b = {"rule": "K5", "tuple_kind": "COUNTS", "own_tuple": True, "slug": "co", "pmid": "2", "label": "RECOVERY",
         "values": {"events_t": 95, "n_t": 324, "events_c": 283, "n_c": 683},
         "doc": {"path": "sub_raw.txt", "format": "text", "text_sha256": sha(tmp_path / "sub_raw.txt")},
         "caption_span": "Table S2: effect of allocation to dexamethasone on 28-day mortality, by respiratory support",
         "header_span": "Dexamethasone (n=2104) Usual care (n=4321)",
         "row_span": "Invasive mechanical ventilation 95/324 (29.3%) 283/683 (41.4%)",
         "outcome_from": "caption", "cells": {"events_t": 0, "events_c": 2},
         "second_reader": {"kind": "SECOND_EXTRACTION",
                           "doc": {"path": "sub_layout.txt", "format": "text",
                                   "text_sha256": sha(tmp_path / "sub_layout.txt")},
                           "row_span": "Invasive mechanical ventilation 95/324 (29.3%) 283/683 (41.4%)"}}
    ok, why = D.verify(b, None, ep("co"))
    assert ok, why


def test_PLANT_k5_a_percentage_cell_is_never_a_count(tmp_path, monkeypatch):
    # codex final5-binding-r1a g1#1: '10% 20%' read as cells '10' / '20' and passed as death counts of n = 200
    setup(tmp_path, monkeypatch)
    doc = ("<caption>Table 2 Hospitalizations and deaths (full-analysis set)</caption><th>FCM ( n = 150)</th>"
           "<th>Placebo ( n = 151)</th><td>Hospitalizations due to worsening HF</td><td>10%</td><td>25%</td>")
    (tmp_path / "doc.txt").write_text(doc, encoding="utf-8")
    b = k5(tmp_path, row_span="Hospitalizations due to worsening HF 10% 25%", cells={"events_t": 0, "events_c": 1})
    assert D.verify(b, None, ep("iv"))[1].startswith("K5_CELL_IS_NOT_THE_COUNT")


def test_PLANT_k5_a_decimal_comma_percentage_cell_is_not_a_count():
    # codex final5-binding-r2 g1#1: '0,5%' split into the count '0' and the percentage '5%'
    assert D._row_cells("Deaths 0,5% 0,7%") == ["0,5%", "0,7%"]
