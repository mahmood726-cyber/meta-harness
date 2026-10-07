"""Plant (search+screen audit, 2026-10-05): an X1 reason must not contradict its own span.

16 served X1 decisions read 'not a randomized controlled trial' while their span cited 'publication types: ...
Randomized Controlled Trial' (scripts/measure_x1_reason_evidence.py); what fired was a TITLE marker (substudy, post hoc,
protocol...). COPPS POAF (PMID 22090167) is the instance. The decision is unchanged (radius: 0 decisions, 16 reasons over
3,201 held decisions); routing a secondary report to its trial family is an owner-decided stage (Codex NR-C28).
Both reason tests fail on the old code."""
from __future__ import annotations

from harness import screen

COPPS = {"id": "22090167", "id_type": "pmid",
         "title": "Colchicine reduces postoperative atrial fibrillation: results of the Colchicine for the Prevention of the "
                  "Postpericardiotomy Syndrome (COPPS) atrial fibrillation substudy.",
         "pubtypes": ["Journal Article", "Multicenter Study", "Randomized Controlled Trial"], "abstract": "x"}
INC = {"population_any": ["cardiac surgery"], "intervention_any": ["colchicine"]}


def test_a_title_marker_on_a_pubmed_rct_is_named_as_such_and_quoted():
    d = screen.screen_record(COPPS, INC, [])
    assert d.decision == "exclude" and d.rule_id == "X1"
    assert d.reason.startswith("not a primary report") and "'substudy'" in d.reason
    assert "substudy" in d.evidence and d.evidence.strip("…") in COPPS["title"]


def test_the_reason_never_says_not_an_rct_while_the_span_says_rct():
    d = screen.screen_record(COPPS, INC, [])
    assert not ("not a randomized controlled trial" in d.reason and "Randomized Controlled Trial" in d.evidence)


def test_a_record_pubmed_does_not_type_an_rct_keeps_the_not_an_rct_reason():
    d = screen.screen_record(dict(COPPS, pubtypes=["Journal Article"]), INC, [])
    assert d.rule_id == "X1" and d.reason.startswith("not a randomized controlled trial")
