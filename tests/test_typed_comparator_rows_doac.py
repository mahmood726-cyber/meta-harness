"""Plants: doac 29795629 Table 1 typed rows (scripts/typed_comparator_rows.py, deterministic regex) pass the tracker's own
re-check (scripts/g1_tracker.typed_comparator_rows: held sha256, span verbatim, every number printed in its span), and a
value that is not printed in its row's span is refused."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import typed_comparator_rows as tcr  # noqa: E402

SLUG = "doac-vte-recurrence"


def test_PLANT_the_reader_reproduces_the_committed_rows_and_the_tracker_accepts_them():
    d = tcr.read(SLUG)
    committed = json.load(open(os.path.join(ROOT, "registry", "comparator_rows", f"{SLUG}.json"), encoding="utf-8"))
    assert d == committed                                   # regenerated, never hand-entered
    assert [r["label"] for r in d["rows"]] == ["RE-COVER", "EINSTEIN-DVT", "AMPLIFY", "Hokusai-VTE", "RE-COVER II"]
    assert (d["rows"][3]["events_t"], d["rows"][3]["n_t"], d["rows"][3]["events_c"], d["rows"][3]["n_c"]) == (130, 4118, 146, 4122)
    got = gt.typed_comparator_rows(SLUG, "29795629")
    assert got is not None and len(got["rows"]) == 5
    assert gt.typed_comparator_rows(SLUG, "24963045") is None          # another comparator: never read


def test_PLANT_a_number_not_printed_in_its_span_refuses_the_whole_file(tmp_path, monkeypatch):
    d = copy.deepcopy(tcr.read(SLUG))
    d["rows"][0]["events_t"] = 31
    p = tmp_path / f"{SLUG}.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    monkeypatch.setattr(gt, "TYPED_COMPARATOR_ROWS", str(tmp_path / "{slug}.json"))
    assert gt.typed_comparator_rows(SLUG, "29795629") is None


def test_PLANT_a_commented_out_row_is_never_read(tmp_path, monkeypatch):
    """codex doac-table1 #1: rows inside XML comments became comparator results."""
    src = os.path.join(ROOT, tcr.READERS[SLUG]["source"])
    raw = open(src, encoding="utf-8").read()
    i = raw.index("<td", raw.index("RE-COVER II") - 400)
    tr = raw.rfind("<tr", 0, raw.index("RE-COVER II"))
    fake = "<!-- <tr><td>FAKE-TRIAL</td><td>2015</td><td>X</td><td>1/10</td><td>Warfarin</td><td>2/10</td><td>50</td><td>40</td></tr> -->"
    p = tmp_path / "held.xml"
    p.write_text(raw[:tr] + fake + raw[tr:], encoding="utf-8")
    cfg = dict(tcr.READERS[SLUG], source=str(p))
    monkeypatch.setitem(tcr.READERS, SLUG, cfg)
    monkeypatch.setattr(tcr, "ROOT", "")
    d = tcr.read(SLUG)
    assert "FAKE-TRIAL" not in [r["label"] for r in d["rows"]] and len(d["rows"]) == 5


def test_PLANT_a_table_with_notes_is_refused_whole(tmp_path, monkeypatch):
    """codex doac-table1-r2: a note could make the numerator a percentage or give different populations per arm."""
    import pytest
    src = os.path.join(ROOT, tcr.READERS[SLUG]["source"])
    raw = open(src, encoding="utf-8").read()
    end = raw.index("</table-wrap>", raw.index('id="pone.0197583.t001"'))
    p = tmp_path / "held.xml"
    p.write_text(raw[:end] + "<table-wrap-foot><p>Events are % of the safety population.</p></table-wrap-foot>" + raw[end:],
                 encoding="utf-8")
    monkeypatch.setitem(tcr.READERS, SLUG, dict(tcr.READERS[SLUG], source=str(p)))
    monkeypatch.setattr(tcr, "ROOT", "")
    with pytest.raises(SystemExit):
        tcr.read(SLUG)


def test_PLANT_any_xref_and_a_changed_caption_refuse(tmp_path, monkeypatch):
    """codex doac-table1-r3: #1 a single-quoted / spaced table-fn xref escaped the note guard; #2 a population qualifier
    in the caption was ignored. Now: any <xref> refuses, and the caption is pinned."""
    import pytest
    src = os.path.join(ROOT, tcr.READERS[SLUG]["source"])
    raw = open(src, encoding="utf-8").read()
    i = raw.index("RE-COVER II")
    for mutated in (raw[:i] + "<xref ref-type = 'table-fn' rid='n1'>a</xref>" + raw[i:],
                    raw.replace("primary efficacy outcomes of the Phase 3 trials included.",
                                "primary efficacy outcomes of the Phase 3 trials included (safety population).", 1)):
        p = tmp_path / "held.xml"
        p.write_text(mutated, encoding="utf-8")
        monkeypatch.setitem(tcr.READERS, SLUG, dict(tcr.READERS[SLUG], source=str(p)))
        monkeypatch.setattr(tcr, "ROOT", "")
        with pytest.raises(SystemExit):
            tcr.read(SLUG)


def test_PLANT_population_qualifiers_in_cells_and_ids_inside_other_attributes_refuse(tmp_path, monkeypatch):
    """codex doac-table1-r4: #1 a population qualifier in an arm cell; #2 id="..." inside another attribute's value
    selected an unrelated earlier table."""
    import pytest
    src = os.path.join(ROOT, tcr.READERS[SLUG]["source"])
    raw = open(src, encoding="utf-8").read()
    decoy = ('<table-wrap id="decoy" title=\'x id="pone.0197583.t001"\'><caption><p>x</p></caption>'
             '<table><tr><td>a</td></tr></table></table-wrap>')
    k = raw.index("<table-wrap")
    for mutated in (raw.replace(">Enoxaparin followed by VKA<",
                                ">Enoxaparin followed by VKA (safety population)<", 1),
                    raw[:k] + decoy + raw[k:]):
        p = tmp_path / "held.xml"
        p.write_text(mutated, encoding="utf-8")
        monkeypatch.setitem(tcr.READERS, SLUG, dict(tcr.READERS[SLUG], source=str(p)))
        monkeypatch.setattr(tcr, "ROOT", "")
        if mutated is not raw and "safety population" in mutated:
            with pytest.raises(SystemExit):
                tcr.read(SLUG)
        else:
            assert len(tcr.read(SLUG)["rows"]) == 5          # the decoy's quoted id is never the table's id
