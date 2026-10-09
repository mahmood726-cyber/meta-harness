"""scripts/g1_final5_typed.py: the deterministic final-5 readers (codex final5-binding-r1a g1#4, g1#5)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_final5_typed as T  # noqa: E402


def _engage(tmp_path, groups):
    d = {"tables": {
        "outcomes.txt": [{"id": "1", "outcome_type": "PRIMARY", "title": "Stroke or systemic embolism (SEE)", "population": "ITT set"}],
        "result_groups.txt": [{"id": str(i), "title": g} for i, g in enumerate(groups, 10)],
        "outcome_analyses.txt": [{"id": "a", "outcome_id": "1", "param_type": "HR", "param_value": "0.87",
                                  "ci_percent": "95", "ci_lower_limit": "0.7", "ci_upper_limit": "1.0"}],
        "outcome_analysis_groups.txt": [{"outcome_analysis_id": "a", "result_group_id": str(i)}
                                        for i, _ in enumerate(groups, 10)]}}
    p = tmp_path / "outputs" / "k_gap" / "g1_binding"
    p.mkdir(parents=True)
    (p / "engage_aact_rows.json").write_text(json.dumps(d), encoding="utf-8")


def test_PLANT_engage_high_dose_v_low_dose_is_not_high_dose_v_warfarin(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    _engage(tmp_path, ["High Dose Edoxaban 60 mg", "Low Dose Edoxaban 30 mg"])
    r = T.engage_aact()
    assert r["result"] == "NOT_FOUND" and "NOT_V_WARFARIN" in r["analyses"][0]["why"]


def test_engage_high_dose_v_warfarin_95_itt_primary_is_found(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    _engage(tmp_path, ["High Dose Edoxaban/Placebo Warfarin", "Warfarin/Placebo Edoxaban"])
    assert T.engage_aact()["result"] == "FOUND"


def test_PLANT_codex_absence_is_never_asserted_without_reading_the_evidence(tmp_path, monkeypatch):
    # codex final5-binding-r1a g1#5: the routes were fixed strings; with nothing held they still said NOT_FOUND
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", str(tmp_path / "no-snapshot"))
    r = T.codex_28d()
    assert r["result"] == "NOT_CHECKED" and all(x["outcome"].startswith("NOT_CHECKED") for x in r["routes"])


def test_PLANT_engage_another_primary_endpoint_is_not_stroke_or_see(tmp_path, monkeypatch):
    # codex final5-binding-r1b g1#4: a PRIMARY analysis of another endpoint passed as the stroke/SEE result
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    _engage(tmp_path, ["High Dose Edoxaban/Placebo Warfarin", "Warfarin/Placebo Edoxaban"])
    p = tmp_path / "outputs" / "k_gap" / "g1_binding" / "engage_aact_rows.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["tables"]["outcomes.txt"][0]["title"] = "Major bleeding"
    p.write_text(json.dumps(d), encoding="utf-8")
    r = T.engage_aact()
    assert r["result"] == "NOT_FOUND" and "NOT_STROKE_OR_SEE" in " ".join(r["analyses"][0]["why"])


def _held(tmp_path, abstract, idx_entry):
    c = tmp_path / "cache" / "corticosteroids-covid19-mortality"
    c.mkdir(parents=True)
    rec = {"id": "32876695"} if abstract is None else {"id": "32876695", "abstract": abstract}
    (c / "records.json").write_text(json.dumps({"records": [rec]}), encoding="utf-8")
    o = tmp_path / "outputs" / "k_gap"
    o.mkdir(parents=True, exist_ok=True)
    (o / "fulltext_index.json").write_text(json.dumps({"32876695": idx_entry} if idx_entry else {}), encoding="utf-8")
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "outcomes.txt").write_text("id|nct_id|title\n1|NCT99999999|x\n", encoding="utf-8")
    return str(snap)


def test_PLANT_codex_prose_counts_are_a_candidate_not_absence(tmp_path, monkeypatch):
    # codex final5-binding-r2 g1#2: '45 patients in the dexamethasone group died' was read as 'no counts'
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, "By day 28, 45 patients in the dexamethasone group and 50 in the "
                                                        "standard care group had died (mortality at 28 days).",
                                              {"state": "FETCH_EMPTY", "copy_licence": "NOT_OPEN"}))
    assert T.codex_28d()["result"] == "CANDIDATE"


def test_PLANT_codex_a_missing_abstract_or_stateless_index_is_not_checked(tmp_path, monkeypatch):
    # codex final5-binding-r2 g1#3 / g1#4
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, None, {"state": "FETCH_EMPTY"}))
    assert T.codex_28d()["result"] == "NOT_CHECKED"


def test_PLANT_codex_an_index_entry_without_a_retrieval_state_is_not_checked(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, "The primary outcome was ventilator-free days.",
                                              {"copy_licence": "CC"}))
    assert T.codex_28d()["result"] == "NOT_CHECKED"


def test_PLANT_codex_patients_assessed_is_not_a_death_count(tmp_path, monkeypatch):
    # codex final5-binding-r3 g1#2
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, "At day 28, 200 patients were assessed for mortality.",
                                              {"state": "FETCH_EMPTY", "copy_licence": "NOT_OPEN"}))
    assert T.codex_28d()["result"] == "NOT_FOUND"


def test_PLANT_codex_mortality_before_the_number_is_a_candidate(tmp_path, monkeypatch):
    # codex final5-binding-r4 g1#3
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, "At 28 days, mortality occurred in 45 patients in the treatment "
                                                        "arm and 40 patients in the control arm.",
                                              {"state": "FETCH_EMPTY", "copy_licence": "NOT_OPEN"}))
    assert T.codex_28d()["result"] == "CANDIDATE"


def test_PLANT_engage_a_wider_composite_is_not_stroke_or_see(tmp_path, monkeypatch):
    # captain codex final5-binding-captain g1#4
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    _engage(tmp_path, ["High Dose Edoxaban/Placebo Warfarin", "Warfarin/Placebo Edoxaban"])
    p = tmp_path / "outputs" / "k_gap" / "g1_binding" / "engage_aact_rows.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["tables"]["outcomes.txt"][0]["title"] = "Stroke, Systemic Embolism, or Cardiovascular Death"
    p.write_text(json.dumps(d), encoding="utf-8")
    assert T.engage_aact()["result"] == "NOT_FOUND"


def test_PLANT_codex_the_number_of_deaths_was_is_a_candidate(tmp_path, monkeypatch):
    # captain codex final5-binding-captain g1#5
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, "At 28 days, the number of deaths was 45 with dexamethasone and "
                                                        "50 with usual care.",
                                              {"state": "PUBLISHER_DISALLOWS_XML"}))
    assert T.codex_28d()["result"] == "CANDIDATE"


def test_PLANT_engage_death_as_a_competing_risk_is_not_a_component(tmp_path, monkeypatch):
    # codex final5-binding-v12-r1 g1#2
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    _engage(tmp_path, ["High Dose Edoxaban/Placebo Warfarin", "Warfarin/Placebo Edoxaban"])
    p = tmp_path / "outputs" / "k_gap" / "g1_binding" / "engage_aact_rows.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["tables"]["outcomes.txt"][0]["title"] = "Stroke or systemic embolism, with death as a competing risk"
    p.write_text(json.dumps(d), encoding="utf-8")
    assert T.engage_aact()["result"] == "FOUND"


def test_PLANT_codex_a_decimal_duration_is_not_a_count(tmp_path, monkeypatch):
    # codex final5-binding-v12-r1 g1#3
    monkeypatch.setattr(T, "ROOT", str(tmp_path))
    monkeypatch.setenv("AACT_SNAPSHOT", _held(tmp_path, "Mortality at 28 days was reported; median time to death was "
                                                        "28.5 days.", {"state": "PUBLISHER_DISALLOWS_XML"}))
    assert T.codex_28d()["result"] == "NOT_FOUND"
