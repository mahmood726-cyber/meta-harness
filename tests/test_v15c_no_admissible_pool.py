"""Empty pools must disclose enforcement, using synthetic extraction/decision fixtures."""
import json

import pytest

from harness import enforcement, pipeline


SPEC = {"name": "Death", "keywords": ["death"], "estimand": "RR", "primary": True}
ABSTRACT = "Drug reduced death (RR 0.80, 95% CI 0.70 to 0.90)."


def build(monkeypatch, tmp_path, decisions, abstract=ABSTRACT):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps({
        "signed": {"packet_sha256": enforcement.PACKET_SHA256, "state": "SEEN_AND_SIGNED"},
        "rows": decisions,
    }), encoding="utf-8")
    real_apply = enforcement.apply
    monkeypatch.setattr(enforcement, "apply", lambda slug, spec, trials:
                        real_apply(slug, spec, trials, path=str(path)))
    included = [{"id": rid, "id_type": "pmid", "label": "Synthetic " + rid} for rid in ("1", "2")]
    records = {r["id"]: {"abstract": abstract} for r in included}
    return pipeline._build_outcome(SPEC, "efficacy", included, records, ["drug"], ["placebo"],
                                   slug="synthetic-enforcement")


@pytest.mark.parametrize("decision", ["REFUSE", "ADMIT"])
def test_all_rows_removed_by_enforcement(monkeypatch, tmp_path, decision):
    rows = [{"slug": "synthetic-enforcement", "outcome": "Death", "id": "PMID " + rid,
             "decision": decision, "kind": "refused_on_evidence", "basis": "Synthetic basis " + rid,
             "served": {"effect": 0.5, "ci_low": 0.4, "ci_high": 0.6}} for rid in ("1", "2")]
    out = build(monkeypatch, tmp_path, rows)
    assert out["trials"] == []
    assert len(out["declared_absent_trials"]) == 2
    result = out["result"]
    assert result["present"] is False
    assert result["reason"].startswith("No admissible pooled result:")
    assert "2 rows" in result["reason"]
    assert result["reason"].endswith("No inadmissible number is served.")
    assert result["no_admissible_pool"] is True
    expected_decision = "REFUSE" if decision == "REFUSE" else "ABSTAIN-not-the-signed-numbers"
    assert result["removed_by_enforcement"] == [
        {"id": r["id"], "decision": expected_decision, "basis": r["basis"]} for r in rows]
    for row in rows:
        assert row["id"] in result["reason"]
        assert row["basis"] in result["reason"]
    assert expected_decision in result["reason"]
    assert not {"estimate", "effect", "ci", "ci_low", "ci_high"}.intersection(result)
    assert result["reported_not_extracted"] is True
    assert result["reported_by"] == ["1", "2"]


@pytest.mark.parametrize("abstract,reported", [("Death was assessed.", True), ("Safety was assessed.", False)])
def test_non_enforcement_empty_reason_unchanged(monkeypatch, tmp_path, abstract, reported):
    result = build(monkeypatch, tmp_path, [], abstract)["result"]
    if reported:
        reason = ("REPORTED but not extractable as a pooled value: 1, 2"
                  " mention this outcome in the committed abstract, but without arm counts or an "
                  "effect+CI in an extractable form (e.g. a bare percentage with no denominator). This "
                  "outcome is NOT absent — it is reported-but-not-poolable from the committed source; "
                  "full-text acquisition would recover the countable form.")
    else:
        reason = ("no included trial reported this outcome with a percentage-corroborated "
                  "count or an effect+CI in its abstract")
    assert result["present"] is False
    assert result["reason"] == reason
    assert "no_admissible_pool" not in result
    assert "removed_by_enforcement" not in result
