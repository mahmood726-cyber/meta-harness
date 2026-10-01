"""Colchicine review (external reviewer, 2026-09-26): COPPS-2's safety table gives separate labelled counts of affected individuals
(any AE 36/180 vs 21/180; GI intolerance 26/180 vs 12/180; discontinuation 39/180 vs 32/180). 36 vs 21 was correctly REJECTED as
not GI intolerance -- but the correctly labelled row was never recovered. Rule: rejecting a wrong-endpoint number triggers a search
for the correctly labelled row in the SAME source table; symptom counts are never summed without knowing the patients are distinct.
The fixture is a labelled TEST FIXTURE (tests/fixtures/copps2_safety_table_fixture.html), not held source bytes: COPPS-2's full
text is not held in this tree, so the served binding cannot be made yet. Plants fired pre-fix (no binder existed)."""
from pathlib import Path

from harness import absence
from harness import evidence_identity as ei

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = (ROOT / "tests" / "fixtures" / "copps2_safety_table_fixture.html").read_text(encoding="utf-8")
GI_TERMS = absence._terms(["gastrointestinal", "diarrh", "adverse effect", "adverse event", "side effect"],
                          "Gastrointestinal adverse effects")        # the served spec's own keywords (topics/colchicine-postop-af.json)


def _bind(raw):
    return ei.bind_labelled_count_row(raw, "25172965", "fixture", GI_TERMS, absence._matches_term,
                                      outcome_name="Gastrointestinal adverse effects")


def test_gi_intolerance_binds_to_26_vs_12_never_36_vs_21():
    b = _bind(FIXTURE)
    assert b["state"] == "BOUND", b
    arms = [(a["events"], a["n"]) for a in b["row"]["arms"]]
    assert arms == [(26, 180), (12, 180)], arms
    assert (36, 180) not in arms and (21, 180) not in arms


def test_an_any_adverse_event_row_never_stands_for_a_specific_endpoint():
    only_any = FIXTURE.replace("<tr><td>Gastrointestinal intolerance</td><td>26/180 (14.4)</td><td>12/180 (6.7)</td></tr>", "")
    assert _bind(only_any)["state"] == "NOT_FOUND"


def test_symptom_rows_are_never_summed_into_the_outcome():
    # SYNTHETIC control (round numbers, no trial): symptoms only, no GI-intolerance row -- a sum would count a patient with both
    # nausea and diarrhoea twice, so the binder must refuse rather than add them
    synthetic = ("<table-wrap><table><thead><tr><th>Event</th><th>Drug (n = 100)</th><th>Placebo (n = 100)</th></tr></thead><tbody>"
                 "<tr><td>Nausea</td><td>10/100 (10.0)</td><td>5/100 (5.0)</td></tr>"
                 "<tr><td>Vomiting</td><td>8/100 (8.0)</td><td>4/100 (4.0)</td></tr></tbody></table></table-wrap>")
    b = _bind(synthetic)
    assert b["state"] == "NOT_FOUND" and "not summed" in b["why"], b


def test_a_symptom_keyword_row_does_not_outrank_the_row_named_by_the_outcome():
    # 'diarrh' is one of the outcome's keywords, but a diarrhoea row is a COMPONENT; the GI-intolerance row is the outcome
    with_symptom = FIXTURE.replace("</tbody>", "<tr><td>Diarrhea</td><td>20/180 (11.1)</td><td>9/180 (5.0)</td></tr></tbody>")
    b = _bind(with_symptom)
    assert b["state"] == "BOUND" and b["row"]["label"] == "Gastrointestinal intolerance", b


def test_the_rejected_number_is_36_vs_21_in_the_held_abstract():
    # the refusal on the served page stays correct: the held abstract's only counts are the any-AE counts
    import json
    rv = json.loads((ROOT / "docs" / "reviews" / "colchicine-postop-af" / "review.json").read_text(encoding="utf-8"))
    gi = next(o for o in rv["outcomes"] if o["name"] == "Gastrointestinal adverse effects")
    row = next(d for d in gi["declared_absent_trials"] if str(d.get("id")).endswith("25172965"))
    assert row["reason_code"] == "REFUSED_ON_EVIDENCE" and "36 versus 21" in row["reason"]
