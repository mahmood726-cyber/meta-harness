"""Synthetic permanent plants: synthesis eligibility is not ledger completeness."""
import copy
import json

from harness import gate, harms, page


def fixture():
    outcome = {"name": "Synthetic bleeding", "kind": "harm", "trials": [
        {"id": "fixture-a", "label": "Fixture A", "source": "Synthetic effect span"}
    ], "declared_absent_trials": [{"id": "fixture-b", "label": "Fixture B",
        "reason_code": "REFUSED_ON_EVIDENCE", "reason": "Synthetic incompatible endpoint",
        "source_span": "Synthetic bleeding reported"}],
        "result": {"estimate": 0.123456, "ci_low": 0.1, "ci_high": 0.2, "k": 1}}
    harms.annotate_outcome(outcome, {"name": "bleeding", "keywords": ["bleeding"]}, [],
                           {"fixture-b": {"abstract": "Synthetic bleeding reported"}})
    return outcome


def write_review(path, outcome):
    (path / "review.json").write_text(json.dumps({"outcomes": [outcome]}), encoding="utf-8")


def test_typed_refusal_quantitative_plant(tmp_path):
    outcome = fixture()
    write_review(tmp_path, outcome)
    planted = '<h4>Synthetic bleeding</h4><p>Pooled estimate 0.123456</p>'
    assert gate.check_harms_synthesis_gated(str(tmp_path), planted)
    assert "0.123" not in page._outcome_block(outcome, show_inputs=False)
    assert "HARMS EXTRACTION INCOMPLETE" in page._outcome_block(outcome)


def test_refusal_relabelled_as_unresolved_plant(tmp_path):
    outcome = fixture()
    write_review(tmp_path, outcome)
    assert gate.check_harms_complete(str(tmp_path)) == []
    assert outcome["declared_absent_trials"][0]["harm_absence_state"] == harms.RETRIEVED_REFUSED_WITH_REASON
    planted = copy.deepcopy(outcome)
    planted["declared_absent_trials"][0]["harm_absence_state"] = harms.KNOWN_REPORTED_NOT_YET_EXTRACTED
    planted["result"]["harms_incomplete"] = True
    planted["result"]["known_reported_not_yet_extracted"] = planted["declared_absent_trials"]
    write_review(tmp_path, planted)
    assert gate.check_harms_complete(str(tmp_path))
    print("REGRESSION PLANT: relabelled refusal -> check_harms_complete REFUSED")


def test_unsupported_adjustment_plant(tmp_path):
    outcome = fixture()
    outcome["trials"][0]["design"] = {"estimator_source": "PUBLISHED_UNADJUSTED"}
    write_review(tmp_path, outcome)
    assert gate.check_adjustment_span_backed(str(tmp_path))


def test_explicit_nonreporting_refusal_does_not_enter_reporting_ledger():
    outcome = fixture()
    outcome["declared_absent_trials"].append({
        "id": "nonreporter", "reason_code": "REFUSED_ON_EVIDENCE",
        "harm_source_reported": False,
        "harm_absence_state": harms.RETRIEVED_OUTCOME_NOT_REPORTED})
    assert "nonreporter" not in {r["id"] for r in harms.reporting_ledger(outcome)}
