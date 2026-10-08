"""scripts/g1_final5_typed.py: the deterministic final-5 readers (codex final5-binding-r1a g1#4, g1#5)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_final5_typed as T  # noqa: E402


def _engage(tmp_path, groups):
    d = {"tables": {
        "outcomes.txt": [{"id": "1", "outcome_type": "PRIMARY", "title": "Stroke or SEE", "population": "ITT set"}],
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
