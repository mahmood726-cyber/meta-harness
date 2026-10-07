"""Plants (search lane, 7 Oct): the five findings of the captain's codex review of the search range 207166d6c..9c72f26bb
(record mc-0effd237, gpt-6-astra). Each test is the finding's own failing input; each failed on 9c72f26b.

  P1 g1_expanded_search.run          a newly fetched record collapsed by dedup inherited the trial's SERVED include
  P0 g1_expanded_dual_codex.items    the false-exclusion extrapolation counted comparator excludes in its population
  P2 g1_expanded_dual_codex.items    a record with no held text vanished from the review inventory
  P1 both dual-codex mains           'adjudicated' counted adjudications NEEDED, pending ones included
  P0 g1_search_screen_report         the expanded-search reading was hard-coded prose, not derived from the results
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]

import g1_expanded_dual_codex as EDC  # noqa: E402
import g1_expanded_search as ES  # noqa: E402
import g1_screen_dual_codex as SDC  # noqa: E402
import g1_search_screen_report as REP  # noqa: E402
from harness import acquisition, fetch, pipeline, screen  # noqa: E402


def test_p1_a_dedup_collapsed_new_record_never_inherits_the_served_include(tmp_path, monkeypatch):
    files = {"records.json": {"records": [{"id": "101"}]}, "fixture.json": {},
             "SEARCH_SCREEN_AUDIT.json": {"topics": [{"slug": "fixture", "trials": [
                 {"kind": "ELIGIBLE", "label": "T", "pmids": ["101", "103"], "search": "MISSED", "screen": "INCLUDED",
                  "screen_include": {"record": "101"}}]}]}}
    monkeypatch.setattr(ES, "_j", lambda p: files[os.path.basename(p)])
    monkeypatch.setattr(ES, "chosen", lambda slug: {"query": "Q"})
    monkeypatch.setattr(ES, "TEXTS", str(tmp_path / "texts"))
    monkeypatch.setattr(ES, "OUT", str(tmp_path / "out"))
    monkeypatch.setattr(acquisition, "esearch_all", lambda q, sleep=0: {"ids": ["102", "103"], "count": 2})
    monkeypatch.setattr(fetch, "_efetch", lambda ids: [{"id": i} for i in ids])
    monkeypatch.setattr(pipeline, "_dedup", lambda d, piv=None: [{"id": "102"}])
    monkeypatch.setattr(screen, "run", lambda m, c: {"decisions": [{"id": "102", "decision": "exclude", "rule_id": "X1"}]})
    ES.run("fixture")
    out = json.load(open(tmp_path / "out" / "fixture.json", encoding="utf-8"))
    rec = {r["pmid"]: r for r in out["records"]}
    assert rec["103"]["rule_id"] == "X-DEDUP"
    d = {x["pmid"]: x for x in out["trials"][0]["screen_decisions"]}
    assert d["103"]["decision"] != "include" and d["103"]["rule_id"] == "X-DEDUP", d
    assert out["recall"]["newly_identified_and_screen_included"] == 0


def _edc_fixture(tmp_path, monkeypatch, records, trials, texts):
    (tmp_path / "exp").mkdir()
    (tmp_path / "texts").mkdir()
    json.dump({"records": records, "trials": trials}, open(tmp_path / "exp" / "fixture.json", "w", encoding="utf-8"))
    json.dump(texts, open(tmp_path / "texts" / "fixture.records.json", "w", encoding="utf-8"))
    monkeypatch.setattr(EDC, "EXP", tmp_path / "exp")
    monkeypatch.setattr(EDC, "TEXTS", tmp_path / "texts")
    monkeypatch.setattr(EDC, "TOPICS", ("fixture",))


def _rec(i):
    return {"id": i, "id_type": "pmid", "title": f"t{i}", "abstract": f"a{i}", "pubtypes": []}


def test_p0_the_extrapolation_population_is_the_sampling_frame_not_the_frame_plus_comparators(tmp_path, monkeypatch):
    _edc_fixture(tmp_path, monkeypatch,
                 [{"pmid": "1", "decision": "exclude", "rule_id": "X2", "held_sha256": "a" * 64},
                  {"pmid": "2", "decision": "exclude", "rule_id": "X2", "held_sha256": "b" * 64}],
                 [{"label": "T", "newly_identified": True,
                   "screen_decisions": [{"pmid": "2", "source": "rule screen (new record)"}]}],
                 [_rec("1"), _rec("2")])
    its, _missing = EDC.items()
    sample = [i for i in its if i["sample_kind"] == "EXCLUDE_SAMPLE"]
    assert [i["record"] for i in sample] == ["1"]
    assert all(i["n_excludes_total"] == 1 for i in sample)      # the frame the rate is estimated on


def test_p2_a_record_with_no_held_text_is_listed_unreviewable_not_dropped(tmp_path, monkeypatch):
    _edc_fixture(tmp_path, monkeypatch, [{"pmid": "1", "decision": "include", "rule_id": "INCLUDE", "held_sha256": "a" * 64}],
                 [], [])
    its, missing = EDC.items()
    assert its == [] and missing == [{"slug": "fixture", "record": "1", "sample_kind": "RULE_INCLUDE",
                                      "why": "no held text for this PMID (expanded-search text store)"}]


def test_p1_adjudications_are_counted_when_done_not_when_needed():
    need = [{"item_id": "a", "adjudicator": {"v": {"model_decision": "ELIGIBLE"}}}, {"item_id": "b"}]
    for mod in (SDC, EDC):
        assert mod.adjudication_counts(need) == {"needed": 2, "completed": 1, "pending": 1}


def test_p0_the_expanded_reading_is_derived_from_the_results():
    exps = {s: {"esearch": {"count": 10}, "new_records": 0,
                "rule_screen": {"include": 0, "exclude": 0, "dedup_collapsed": 0},
                "recall": {"identified_before": 1, "identified_after": 1, "eligible": 1, "newly_identified": 0,
                           "newly_identified_and_screen_included": 0}} for s in ("a", "b", "c", "d")}
    edc = {"sample_n": 100, "topics": {s: {"exclude_sample": {"rate": 0.0, "wilson95": [0.0, 0.037],
                                                              "extrapolated_false_exclusions": 0.0, "excludes_total": 100},
                                           "rule_includes_final": {"ELIGIBLE": 0, "INELIGIBLE": 0, "UNRESOLVED": 0},
                                           "comparator_trials": []} for s in exps}}
    text = "\n".join(REP.expanded_section(exps, edc))
    assert "omega3 doubles" not in text and "dozens" not in text
    assert "no topic identified an additional eligible comparator trial" in text
    assert "no false exclusion was found in any exclude sample" in text
