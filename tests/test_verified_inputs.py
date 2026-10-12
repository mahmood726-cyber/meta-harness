"""Synthetic fixtures for row-scoped span failures; never clinical inputs."""
import json

import pytest

from harness import absence, pipeline, verified_inputs


@pytest.mark.parametrize("filename,kind,numbers", [
    ("verified_effects.json", "extracted_effect",
     {"effect": 0.5, "ci_low": 0.2, "ci_high": 0.9, "scale": "RR"}),
    ("verified_arms.json", "extracted_counts", {"ai": 1, "n1i": 20, "ci": 2, "n2i": 20}),
])
@pytest.mark.parametrize("document_ref", ["records.json", "missing.txt"])
def test_span_refusal_blocks_fallbacks_and_preserves_evidence(tmp_path, monkeypatch, filename, kind, numbers,
                                                            document_ref):
    topic = tmp_path / "synthetic"
    topic.mkdir()
    held = "Synthetic harm: risk ratio 0.5 (95% CI 0.2 to 0.9)."
    span = held + " A stale suffix, although the numeric tuple still matches."
    (topic / "records.json").write_text(json.dumps({"records": [
        {"id": "fixture", "abstract": held}]}), encoding="utf-8")
    entry = {"outcome": "Synthetic harm", "kind": kind, **numbers,
             "source_span": span, "document_ref": document_ref, "source_level": 1}
    path = topic / filename
    path.write_text(json.dumps({"fixture": entry}), encoding="utf-8")
    loaded = verified_inputs.load("synthetic", cache_root=tmp_path)
    evidence = loaded[filename]["fixture"]["span_refusal"]
    assert evidence["reason_code"] == "ENDPOINT_UNBOUND"
    assert evidence["source_span"] == span
    assert evidence["document_ref"] == document_ref
    assert "source_span absent from held document" in evidence["reason"]

    def no_candidates(*args, **kwargs):
        pytest.fail("A refused extraction reached source/estimand selection")

    monkeypatch.setattr(pipeline, "_source_effect_candidates", no_candidates)
    out = pipeline._build_outcome(
        {"name": "Synthetic harm", "keywords": ["harm"], "estimand": "RR"}, "harm",
        [{"id": "fixture", "id_type": "pmid"}], {"fixture": {"abstract": held}}, ["drug"], ["placebo"],
        verified_effects=loaded["verified_effects.json"], verified_arms=loaded["verified_arms.json"],
        dose_selection={"fixture": {"outcome": "Synthetic harm", "effect": 0.5,
                                    "ci_low": 0.2, "ci_high": 0.9, "scale": "RR"}})
    assert not out["trials"]
    row, = out["declared_absent_trials"]
    assert row["id"] == "PMID fixture"
    assert row["span_refusals"] == [evidence]
    annotation = absence.classify_reason(["harm"], held, row=row, reason=row["reason"])
    assert annotation["reason_code"] == "ENDPOINT_UNBOUND"
    assert annotation["state"] == "EXTRACTION_DEBT"

    # Revalidation clears even a serialized stale refusal once the exact span is restored.
    entry.update(source_span=held, document_ref="records.json", span_refusal=evidence)
    path.write_text(json.dumps({"fixture": entry}), encoding="utf-8")
    assert "span_refusal" not in verified_inputs.load("synthetic", cache_root=tmp_path)[filename]["fixture"]
