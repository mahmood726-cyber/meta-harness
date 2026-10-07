"""Plants (6 Oct, forest lane): the third-reader AUDIT of an accepted comparator figure compares an independent codex
reading with the ACCEPTED agreed rows and pooled row by the reader's own agreement rule (printed rounding; counts exact).
It reports; it never changes an acceptance."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_forest_reader as gfr  # noqa: E402

ACC = [{"label": "TRIAL A", "effect": "0.80", "lower": "0.60", "upper": "1.07", "events_t": 10, "n_t": 100,
        "events_c": 12, "n_c": 99},
       {"label": "TRIAL B", "effect": "1.10", "lower": "0.90", "upper": "1.34", "events_t": None, "n_t": None,
        "events_c": None, "n_c": None}]
POOL = {"effect": "0.95", "lower": "0.80", "upper": "1.12"}


def _reading(rows, pooled):
    return {"legible": True, "row_kind": "study", "rows": rows, "pooled": pooled, "measure": "RR"}


def test_identical_reading_audits_clean():
    a = gfr.audit_compare(ACC, POOL, _reading([dict(r) for r in ACC], dict(POOL)))
    assert a["state"] == "AUDIT_AGREES" and a["disagreements"] == [] and a["rows_agreeing"] == 2


def test_a_count_difference_a_missing_row_and_a_pooled_difference_are_findings():
    rows = [dict(ACC[0], events_t=11)]                       # TRIAL A count differs; TRIAL B missing
    a = gfr.audit_compare(ACC, POOL, _reading(rows, dict(POOL, effect="0.97")))
    assert a["state"] == "AUDIT_DISAGREES"
    whys = {d["label"]: d["why"] for d in a["disagreements"]}
    assert "EVENTS_T_DISAGREES" in whys["TRIAL A"] and whys["TRIAL B"] == "ONLY_IN_ACCEPTED"
    assert a["pooled"]["state"] == "POOLED_DISAGREES"


def test_rounding_within_printed_precision_is_agreement():
    rows = [dict(ACC[0], effect="0.8"), dict(ACC[1])]
    assert gfr.audit_compare(ACC, POOL, _reading(rows, dict(POOL)))["state"] == "AUDIT_AGREES"


def test_a_zero_count_agrees_with_zero_whatever_its_json_type():
    # 'str(x or "")' turned the NUMBER 0 into '' (zero is falsy): every zero-event row read as a disagreement
    assert gfr.agree_count(0, "0") == (True, 0)
    assert gfr.agree_count(0, 0) == (True, 0)
    assert gfr.agree_count("0", 0) == (True, 0)
    assert gfr.agree_count(None, None) == (True, None)
    assert gfr.agree_count(0, None)[0] is False


def test_audit_scope_selects_accepted_figures_of_that_section_only():
    o = {"results": {"s1": {"state": "ACCEPTED"}, "s2": {"state": "REFUSED"}},
         "meta_results": {"s1::11": {"state": "ACCEPTED"}, "s1::12::F2": {"state": gfr.SECOND_SOURCE_ONLY},
                          "s1::13": {"state": "REFUSED"}}}
    assert sorted(gfr.audit_targets(o, "comparator")) == ["s1"]
    assert sorted(gfr.audit_targets(o, "meta")) == ["s1::11", "s1::12::F2"]


def test_extra_audit_rows_with_every_accepted_row_agreeing_is_not_a_disagreement():
    rows = [dict(r) for r in ACC] + [{"label": "TRIAL C", "effect": "1.0", "lower": "0.5", "upper": "2.0",
                                       "events_t": "1", "n_t": "10", "events_c": "1", "n_c": "10"}]
    a = gfr.audit_compare(ACC, POOL, _reading(rows, dict(POOL)))
    assert a["state"] == "AUDIT_AGREES_ACCEPTED_ROWS" and a["extra_audit_rows"] == ["TRIAL C"]
    assert a["disagreements"] == []


def test_the_audit_compares_only_the_same_figure_and_panel():
    acc = {"figure": {"fig_id": "F2", "panel": "A"}, "image": {"sha256": "x"}}
    assert gfr.audit_same_figure({"figure": {"fig_id": "F2", "panel": "A"}, "image_sha256": "x"}, acc)
    assert not gfr.audit_same_figure({"figure": {"fig_id": "F2", "panel": "B"}, "image_sha256": "x"}, acc)
    assert not gfr.audit_same_figure({"figure": {"fig_id": "F2", "panel": "A"}, "image_sha256": "y"}, acc)


def test_a_later_skip_never_erases_an_accepted_recorded_result():
    # ae9a3075 (5 Oct): a later run whose figure re-selection failed moved ACCEPTED tocilizumab reads 33161150 and
    # 34019122 into meta_skipped, silently dropping 14 secondary rows; the accepted result rests on records and stays
    sec = {"results": {}, "skipped": {}, "meta_results": {"t::1": {"state": "ACCEPTED", "rows": 9}}, "meta_skipped": {}}
    gfr.merge_skips(sec, {"t::1": {"why": "NO_OUTCOME_FOREST_FIGURE"}, "t::2": {"why": "NO_JATS"}})
    assert sec["meta_results"]["t::1"]["state"] == "ACCEPTED"
    assert sec["meta_results"]["t::1"]["later_skip"] == {"why": "NO_OUTCOME_FOREST_FIGURE"}
    assert "t::1" not in sec["meta_skipped"] and sec["meta_skipped"]["t::2"] == {"why": "NO_JATS"}


def test_a_wrong_intervention_verdict_still_refuses_an_accepted_figure():
    # 6 Oct: the restore above also kept corticosteroids 35343397 (an IL-6 antagonist meta) and tocilizumab 35197981
    # (convalescent plasma) ACCEPTED. Failing to re-select a figure is not a verdict; INTERVENTION_NOT_THE_TOPICS is a
    # gate's verdict about the figure itself and must win
    sec = {"results": {}, "skipped": {}, "meta_results": {"t::1": {"state": "ACCEPTED", "rows": 9}}, "meta_skipped": {}}
    gfr.merge_skips(sec, {"t::1": "INTERVENTION_NOT_THE_TOPICS"})
    assert "t::1" not in sec["meta_results"]
    assert sec["meta_skipped"]["t::1"] == "INTERVENTION_NOT_THE_TOPICS"


def _stored(tmp_path, monkeypatch, img=b"IMG", prompt=b"ORIGINAL PROMPT\n"):
    import base64, hashlib, json
    monkeypatch.setattr(gfr, "ROOT", str(tmp_path))
    monkeypatch.setattr(gfr, "REC_DIR", str(tmp_path / "rec"))
    (tmp_path / "rec").mkdir()
    (tmp_path / "img.jpg").write_bytes(img)
    rec = {"record_id": "mc-x", "prompt": {"b64": base64.b64encode(prompt).decode(), "bytes": str(len(prompt)),
                                           "sha256": hashlib.sha256(prompt).hexdigest()}}
    (tmp_path / "rec" / "mc-x.json").write_text(json.dumps(rec), encoding="utf-8")
    return {"state": "ACCEPTED", "slug": "t", "pmid": "1", "figure": {"fig_id": "F2", "panel": None, "caption": "c"},
            "image": {"ref": "img.jpg", "sha256": hashlib.sha256(b"IMG").hexdigest()},
            "readings": {"codex": {"record_id": "mc-x"}}}


def test_an_accepted_figure_the_selection_cannot_rebuild_is_audited_from_its_own_record(tmp_path, monkeypatch):
    # 6 Oct: 5 accepted figures (tocilizumab 33161150 / 34019122, colchicine 36176989 F11, probiotics 29868585,
    # spironolactone 40959489 F2D) were silently absent from the audit: the current figure selection no longer
    # rebuilds them. The audit reads the SAME image (sha-checked) with the original codex prompt + the audit line
    v = _stored(tmp_path, monkeypatch)
    it = gfr.stored_item("t::1", v)
    assert it["prompt_override"] == b"ORIGINAL PROMPT\n" + gfr.AUDIT_LINE.encode()
    assert it["image_sha256"] == v["image"]["sha256"] and gfr.audit_same_figure(it, v)


def test_a_stored_item_whose_image_changed_is_not_audited(tmp_path, monkeypatch):
    v = _stored(tmp_path, monkeypatch, img=b"OTHER BYTES")
    assert gfr.stored_item("t::1", v) is None


def test_a_skip_for_a_new_comparator_retires_the_old_comparators_accepted_read():
    # 7 Oct: statins / denosumab / melatonin swapped comparators; their ACCEPTED reads were of the RETIRED comparator.
    # merge_skips kept them (an accepted result survives a re-selection failure) -- but a skip for a DIFFERENT pmid is
    # a different artefact: the stale read moves to retired_results, never stays as the topic's comparator read
    sec = {"results": {"t": {"state": "ACCEPTED", "pmid": "111"}}, "skipped": {}, "meta_results": {}, "meta_skipped": {}}
    gfr.merge_skips(sec, {"t": {"pmid": "222", "why": "NO_OUTCOME_FOREST_FIGURE"}})
    assert "t" not in sec["results"] and sec["skipped"]["t"]["pmid"] == "222"
    assert sec["retired_results"]["t::111"]["state"] == "ACCEPTED"


def test_a_missing_figure_tool_skips_that_item_only(monkeypatch):
    # 7 Oct: 'import fitz' failed on the worker inside figure_for and the whole 995-candidate run died
    def boom(*a, **k):
        raise ModuleNotFoundError("No module named 'fitz'", name="fitz")
    monkeypatch.setattr(gfr, "figure_for", boom)
    monkeypatch.setattr(gfr, "jats_path", lambda p: "x")
    monkeypatch.setattr(gfr, "comparator_of", lambda s: "999")
    its, skipped = gfr.items([], False, pairs=[("t", "1")])
    assert its == [] and skipped["t::1"]["why"] == "FIGURE_TOOL_UNAVAILABLE:fitz"
