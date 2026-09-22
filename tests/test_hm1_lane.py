import json
import pytest

from harness import absence, gate, harms, pipeline
from _families import eligible_by_construction  # noqa: E402  (families ELIGIBLE by construction: the admission gate is on by default)


def test_spelled_count_verification_is_lexical_not_percentage_imputation():
    from harness.verify import verify_pooled
    trial = {"ai": 18, "n1i": 245, "ci": 12, "n2i": 222,
             "provenance": "fulltext_verified_arms",
             "source": "Eighteen of 245 participants and 12 of 222 participants had an AE."}
    assert verify_pooled(trial, None)[0] == "verified"
    trial["ai"] = 19
    assert verify_pooled(trial, None)[0] == "not-yet"


def test_hm1_plant(tmp_path):
    spec = {"name": "Any adverse events", "keywords": ["adverse events"]}
    records = {"fixture": {"abstract": "Adverse events were similar between groups."}}
    outcome = {"name": spec["name"], "kind": "harm", "trials": [],
               "declared_absent_trials": [{"id": "fixture", "reason_code": "OUTCOME_NOT_IN_SOURCE"}],
               "result": {"present": False}}
    harms.annotate_outcome(outcome, spec, [{"id": "fixture"}], records)
    (tmp_path / "review.json").write_text(json.dumps({"outcomes": [outcome]}), encoding="utf-8")
    assert "HARMS_INCOMPLETE" in gate.check_harms_complete(str(tmp_path))[0]
    refusal = {"id": "fixture", "absent_kind": "adjudicated_absent",
               "reason_code": absence.REFUSED_ON_EVIDENCE,
               "source_span": records["fixture"]["abstract"],
               "reason": "The source gives a narrative comparison without per-arm counts or effect with CI."}
    refusal.update(absence.classify_reason(spec["keywords"], records["fixture"]["abstract"],
                                          row=refusal, reason=refusal["reason"]))
    outcome["declared_absent_trials"] = [refusal]
    outcome["result"] = {"present": False}
    harms.annotate_outcome(outcome, spec, [{"id": "fixture"}], records)
    assert refusal["harm_absence_state"] == harms.RETRIEVED_REFUSED_WITH_REASON
    (tmp_path / "review.json").write_text(json.dumps({"outcomes": [outcome]}), encoding="utf-8")
    assert gate.check_harms_complete(str(tmp_path)) == []


def test_spurious_refusal_requires_held_span():
    row = {"absent_kind": "adjudicated_absent", "reason_code": absence.SIGNAL_SPURIOUS,
           "source_span": "Historical safety was documented."}
    result = absence.classify_reason(["safety"], row["source_span"], row=row,
                                     reason="Historical strain safety is not this trial's harm result.")
    assert result["reason_code"] == absence.SIGNAL_SPURIOUS
    with pytest.raises(ValueError, match="verbatim"):
        absence.classify_reason(["safety"], "Another source.", row=row, reason="A reason")


def test_multiple_verified_outcomes_are_selected_independently():
    primary = {"outcome": "Efficacy", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10}
    harm = {"outcome": "Harm", "ai": 3, "n1i": 10, "ci": 4, "n2i": 10, "override": True,
            "source": "3 of 10 versus 4 of 10 participants had harm."}
    entries = {"1": [primary, harm]}
    from harness.verified_inputs import normalise
    assert pipeline._verified_for_outcome(entries, "Efficacy") == {"1": normalise(primary)}
    assert pipeline._verified_for_outcome({"1": primary}, "Efficacy") == {"1": normalise(primary)}
    out = pipeline._build_outcome({"name": "Harm", "keywords": ["harm"], "estimand": "RR"},
                                  "harm", [{"id": "1", "id_type": "pmid"}],
                                  {"1": {"abstract": harm["source"]}}, ["drug"], ["placebo"],
                                  verified_arms=entries, family_nodes=eligible_by_construction({"1": {}}))
    assert out["trials"][0]["ai"] == 3
    with pytest.raises(ValueError, match="Duplicate"):
        pipeline._verified_for_outcome({"1": [harm, harm]}, "Harm")


def test_effect_list_and_refusal_do_not_shadow_another_outcome():
    effect = {"outcome": "Harm", "override": True, "effect": 0.8, "ci_low": 0.6,
              "ci_high": 1.1, "scale": "RR", "source": "Harm RR 0.8 (0.6-1.1)."}
    other = {"outcome": "Efficacy", "override": True, "absent": True}
    out = pipeline._build_outcome({"name": "Harm", "keywords": ["harm"], "estimand": "RR"},
                                  "harm", [{"id": "1", "id_type": "pmid"}],
                                  {"1": {"abstract": effect["source"]}}, ["drug"], ["placebo"],
                                  verified_effects={"1": [other, effect]}, family_nodes=eligible_by_construction({"1": {}}))
    assert out["trials"][0]["effect"] == 0.8


def test_missing_effect_list_is_outcome_scoped(tmp_path):
    from harness import missing_effect
    cache = tmp_path / "cache" / "fixture"
    cache.mkdir(parents=True)
    rows = [{"outcome": "Efficacy", "effect": 0.5, "ci_low": 0.3, "ci_high": 0.8},
            {"outcome": "Harm", "effect": 1.5, "ci_low": 1.2, "ci_high": 2.0}]
    (cache / "verified_effects.json").write_text(json.dumps({"1": rows}), encoding="utf-8")
    ambiguous = missing_effect.enrich_from_cache(str(tmp_path), "fixture", [{"id": "1"}])
    assert "effect" not in ambiguous[0]
    scoped = missing_effect.enrich_from_cache(str(tmp_path), "fixture", [{"id": "1", "outcome": "Efficacy"}])
    assert scoped[0]["effect"] == 0.5


def test_hm1_all_new_spans_are_held_and_audited():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    cache = root / "cache" / "probiotics-aad-prevention"
    records = {str(r["id"]): r for r in json.loads((cache / "records.json").read_text(encoding="utf-8"))["records"]}
    audit = json.loads((root / "docs/evidence/override-audit-2026-09-14/overrides.json").read_text(encoding="utf-8"))
    entries = json.loads((cache / "verified_arms.json").read_text(encoding="utf-8"))
    checked = 0
    for pid, value in entries.items():
        for e in value if isinstance(value, list) else [value]:
            if e.get("outcome") not in {"Any adverse events", "Serious adverse events"}:
                continue
            span = e.get("source_span") or e.get("source")
            held = records[pid]["abstract"]
            path = cache / f"ft_{pid}.txt"
            if path.exists():
                held += path.read_text(encoding="utf-8")
            assert span and span in held, (pid, e["outcome"])
            assert any(a["topic"] == cache.name and a["trial"] == pid
                       and a["outcome"] == e["outcome"] and a.get("judgement") for a in audit)
            checked += 1
    assert checked == 58
