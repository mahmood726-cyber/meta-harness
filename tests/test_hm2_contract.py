"""Offline HM2 regression fixtures; synthetic rows never enter review data."""
import json

from harness import absence, gate, harms, pipeline, verify
from _families import eligible_by_construction  # noqa: E402  (families ELIGIBLE by construction: the admission gate is on by default)


def test_hm2_unresolved_fixture_refuses_gate(tmp_path):
    spec = {"name": "Gastrointestinal adverse events", "keywords": ["gastrointestinal"]}
    out = {"name": spec["name"], "kind": "harm", "trials": [],
           "declared_absent_trials": [{"id": "PMID 1", "state": "OUTCOME_NOT_IN_SOURCE"}],
           "result": {"present": False}}
    harms.annotate_outcome(out, spec, [{"id": "1"}],
                           {"1": {"abstract": "Gastrointestinal adverse events were more common."}})
    (tmp_path / "review.json").write_text(json.dumps({"outcomes": [out]}), encoding="utf-8")
    reasons = gate.check_harms_complete(str(tmp_path))
    print("BASE FIXTURE:", *reasons, sep="\n")
    assert reasons and "HARMS_INCOMPLETE" in reasons[0]

    out = {"name": spec["name"], "kind": "harm", "trials": [],
           "declared_absent_trials": [{"id": "PMID 1", "state": absence.REFUSED_ON_EVIDENCE,
               "reason_code": absence.REFUSED_ON_EVIDENCE,
               "source_span": "Gastrointestinal adverse events were more common.",
               "reason": "Narrative comparison without counts or effect and CI."}],
           "result": {"present": False}}
    harms.annotate_outcome(out, spec, [{"id": "1"}],
                           {"1": {"abstract": "Gastrointestinal adverse events were more common."}})
    (tmp_path / "review.json").write_text(json.dumps({"outcomes": [out]}), encoding="utf-8")
    assert gate.check_harms_complete(str(tmp_path)) == []
    assert out["declared_absent_trials"][0]["harm_absence_state"] == harms.RETRIEVED_REFUSED_WITH_REASON
    print("RESOLVED FIXTURE: PASS")


def test_multiple_verified_outcomes_preserve_legacy_and_refusals(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "ROOT", str(tmp_path))
    cache = tmp_path / "cache" / "fixture"
    cache.mkdir(parents=True)
    (cache / 'records.json').write_text(json.dumps({'records': [
        {'id': '1', 'abstract': 'Background gastrointestinal disease was assessed.'}]}), encoding='utf-8')
    entries = {"1": [{"outcome": "Efficacy", "effect": 0.8, "ci_low": 0.6, "ci_high": 1.0},
                     {"outcome": "GI", "override": True, "absent": True,
                      "provenance": absence.SIGNAL_SPURIOUS, "reason": "Background symptom only.",
                      "source_span": "Background gastrointestinal disease was assessed."}],
               "2": {"outcome": "GI", "ai": 1, "n1i": 20, "ci": 2, "n2i": 20}}
    for name, loader in [("verified_arms.json", pipeline._load_verified_arms),
                         ("verified_effects.json", pipeline._load_verified_effects)]:
        (cache / name).write_text(json.dumps(entries), encoding="utf-8")
        loaded = loader("fixture")
        assert pipeline._verified_for_outcome(loaded, "Efficacy")["1"]["effect"] == 0.8
        gi = pipeline._verified_for_outcome(loaded, "GI")
        assert gi["1"]["absent"] and gi["2"]["ai"] == 1
    spec = {"name": "GI", "keywords": ["gastrointestinal"], "estimand": "RR"}
    out = pipeline._build_outcome(spec, "harm", [{"id": "1", "id_type": "pmid"}],
        {"1": {"abstract": "Background gastrointestinal disease was assessed."}},
        ["drug"], ["placebo"], verified_effects=entries, family_nodes=eligible_by_construction({"1": {}}))
    row = out["declared_absent_trials"][0]
    # Efficacy-strand membership annotation must not erase a harm adjudication.
    row["absent_kind"] = "pooled_in_strand"
    ann = absence.classify_reason(spec["keywords"], "Background gastrointestinal disease was assessed.",
        row=row, reason=row["reason"], absent_kind=row["absent_kind"])
    assert ann["reason_code"] == absence.SIGNAL_SPURIOUS
    row.update(ann)
    harms.annotate_outcome(out, spec, [{"id": "1"}],
        {"1": {"abstract": "Background gastrointestinal disease was assessed."}})
    assert not out["result"].get("harms_incomplete")
    assert out["result"]["harm_reporting_trials_n"] == 0
    assert row["harm_source_reported"] is False


def test_written_count_words_are_verified_without_rounding():
    assert verify._digits_in("nine patients of 120", 9, 120)
    assert not verify._digits_in("nineteen patients of 120", 9, 120)
    assert not verify._digits_in("9.7%", 23)


def test_missing_primary_enrichment_selects_primary_from_list(tmp_path):
    from harness import missing_effect
    cache = tmp_path / "cache" / "fixture"
    cache.mkdir(parents=True)
    topics = tmp_path / "topics"
    topics.mkdir()
    (topics / "fixture.json").write_text(json.dumps({"primary_outcome": {"name": "Efficacy"}}), encoding="utf-8")
    (cache / "verified_effects.json").write_text(json.dumps({"1": [
        {"outcome": "Harm", "effect": 2.0}, {"outcome": "Efficacy", "effect": 0.8}]}), encoding="utf-8")
    rows = missing_effect.enrich_from_cache(str(tmp_path), "fixture", [{"id": "1"}])
    assert rows[0]["effect"] == 0.8


def test_analysis_set_mismatch_does_not_evict_before_pooling():
    from harness import eligibility_chain
    cfg = {"include": {"design_double_blind": True, "comparator_any": ["placebo"]},
           "primary_outcome": {"population": "intention-to-treat", "timepoint": "trial end"}}
    contract = eligibility_chain.compile_contract("fixture", cfg,
        "Double-blind OR placebo-controlled.\n**Population** - intention-to-treat.\n**Timepoint** - trial end.")
    spec = {"name": "GI", "keywords": ["gastrointestinal"], "estimand": "RR"}
    out = pipeline._build_outcome(spec, "harm", [{"id": "12345678", "id_type": "pmid"}],
        {"12345678": {"abstract": "Double-blind placebo-controlled trial at trial end; available-case analyzed patients."}},
        ["drug"], ["placebo"], verified_arms={"12345678": {"outcome": "GI", "override": True,
            "ai": 1, "n1i": 20, "ci": 2, "n2i": 20, "source": "1 of 20 versus 2 of 20"}},
        eligibility_contract=contract, family_nodes=eligible_by_construction({"12345678": {}}))
    assert len(out["trials"]) == 1
    admission = eligibility_chain.admission_record(out['trials'][0],
        {'abstract': 'Double-blind placebo-controlled trial at trial end; available-case analyzed patients.'},
        spec, contract)
    assert admission['analysis_set']['axis'] == 'compatibility'
    assert admission['analysis_set']['finding_code'] == 'COMPAT_MISMATCH'


def test_refused_candidate_analysis_sets_render_without_a_pool():
    from harness.page import render_outcome_block, _outcome_unit_counts
    outcome = {"name": "Primary", "kind": "efficacy", "trials": [],
               "declared_absent_trials": [], "result": {"present": False, "reason": "contract refusal"},
               "admission_analysis_sets": {"label": "mixed / trial-defined", "scope": "candidates",
                   "per_trial": [{"trial_id": "fixture", "value": "AVAILABLE_CASE", "verdict": "FAIL"}]}}
    assert _outcome_unit_counts(outcome)["pooled"]["trials"] == 0
    html = render_outcome_block(outcome)
    assert "mixed / trial-defined" in html and "AVAILABLE_CASE" in html


def test_hm2_evidence_spans_are_held_and_all_new_entries_audited():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    items = json.loads((root / "outputs/handover/HM2_item_evidence.json").read_text(encoding="utf-8"))
    audits = json.loads((root / "docs/evidence/override-audit-2026-09-14/overrides.json").read_text(encoding="utf-8"))
    keys = {(x["topic"], x["file"], str(x["trial"]), x["outcome"]) for x in audits}
    for item in items:
        if item["category"] == "unresolved":
            continue
        e = item["entry"]
        path = root / e["document_ref"].split("#")[0]
        source = e.get("source_span") or e["source"]
        if path.name == "records.json":
            recs = json.loads(path.read_text(encoding="utf-8"))["records"]
            assert source in next(r["abstract"] for r in recs if str(r["id"]) == item["pmid"])
        elif path.name == "harms_aact_held.json":
            data = json.loads(path.read_text(encoding="utf-8"))
            assert source == "\n".join("|".join(r.values()) for r in data["result_groups"] + data["reported_events"])
        else:
            assert source in path.read_text(encoding="utf-8")
        assert (item["slug"], item["file"], item["pmid"], item["outcome"]) in keys
