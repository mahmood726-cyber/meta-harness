"""HRM regression plants: synthetic inputs, never research output."""
import json

from harness import design_key, gate, harms, page


def refused_harm():
    return {"name": "Synthetic bleeding", "kind": "harm", "trials": [
        {"id": "fixture-a", "label": "Fixture A", "source": "Synthetic located effect span"}
    ], "declared_absent_trials": [{
        "id": "fixture-b", "label": "Fixture B", "reason_code": "REFUSED_ON_EVIDENCE",
        "reason": "Synthetic incompatible endpoint", "source_span": "Synthetic bleeding reported"
    }], "result": {"estimate": 0.123456, "ci_low": 0.1, "ci_high": 0.2, "k": 1}}


def annotate(out):
    return harms.annotate_outcome(out, {"name": "bleeding", "keywords": ["bleeding"]}, [],
                                  {"fixture-b": {"abstract": "Synthetic bleeding reported"}})


def test_refusal_suppresses_pool_and_preserves_ledger():
    out = annotate(refused_harm())
    html = page._outcome_block(out, show_inputs=False)
    assert "HARMS EXTRACTION INCOMPLETE" in html
    assert "Fixture B" in html and "REFUSED_ON_EVIDENCE" in html
    assert "0.123" not in html


def test_substring_is_not_adjustment_evidence():
    for source in ("A reported hazard ratio", "Unadjusted unrelated analysis", "dose adjustment"):
        trial = {"effect": 1.1, "scale": "HR", "source": source}
        key = design_key.key_for_trial(trial)
        assert key["estimator_source"] == "PUBLISHED_HR"
        assert key["adjustment_status"] == "UNRESOLVED"


def test_gate_refuses_planted_harms_and_adjustment(tmp_path):
    out = annotate(refused_harm())
    out["trials"][0]["design"] = {"estimator_source": "PUBLISHED_UNADJUSTED"}
    (tmp_path / "review.json").write_text(json.dumps({"outcomes": [out]}), encoding="utf-8")
    assert gate.check_harms_synthesis_gated(str(tmp_path), "<h4>Synthetic bleeding</h4><p>Pooled estimate 0.123456</p>")
    assert gate.check_adjustment_span_backed(str(tmp_path))


def test_complete_ledger_retained_and_missing_span_blocks():
    out = refused_harm()
    out["declared_absent_trials"] = []
    annotate(out)
    html = page._outcome_block(out, show_inputs=False)
    assert "Harms extraction ledger" in html
    assert "Single-trial effect" in html
    out["trials"][0].pop("source")
    assert harms.synthesis_incomplete(out)
    assert "Single-trial effect" not in page._outcome_block(out, show_inputs=False)


def test_valid_axis_and_tampered_location(tmp_path):
    trial = {"id": "fixture", "effect": 1.1, "scale": "HR", "source": "Model adjusted for region."}
    trial["adjustment_axis"] = {"status": "ADJUSTED", "source": "synthetic model specification",
                                "span": trial["source"], "start": 0, "end": len(trial["source"])}
    trial["design"] = design_key.key_for_trial(trial)
    assert trial["design"]["adjustment_status"] == "ADJUSTED"
    path = tmp_path / "review.json"
    path.write_text(json.dumps({"outcomes": [{"trials": [trial]}]}), encoding="utf-8")
    assert not gate.check_adjustment_span_backed(str(tmp_path))
    trial["adjustment_axis"]["start"] = 1
    path.write_text(json.dumps({"outcomes": [{"trials": [trial]}]}), encoding="utf-8")
    assert gate.check_adjustment_span_backed(str(tmp_path))


def test_gate_refuses_injected_result_even_with_ledger(tmp_path):
    out = annotate(refused_harm())
    review = {"outcomes": [out]}
    (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    html = '<section class="tab" id="tab-harms"><h3 class="tabname">Harms</h3>' + page._harms(review, False)
    assert not gate.check_harms_synthesis_gated(str(tmp_path), html + "</section>")
    assert gate.check_harms_synthesis_gated(str(tmp_path), html + "<p>Pooled HR 0.5</p></section>")


def test_suppressed_harm_has_no_canonical_quantitative_claim():
    from harness import census
    out = annotate(refused_harm())
    assert not out["result"]["claim"]["present"]
    assert not census._claim_check({"outcomes": [out]})["contradictions"]
