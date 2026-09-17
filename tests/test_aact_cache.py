"""Regression contract: a build must never reach off-tree AACT tables."""
import json
from pathlib import Path

from harness import aact, aact_cache, armcontrast
from harness.page import render_page
from scripts.reproduce_review import replay_core, reproduce

SLUG = "tocilizumab-covid19-mortality"


def forbid_snapshot(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("build attempted a snapshot read")
    for name in ("snapshot_dir", "_table", "_iter_rows"):
        monkeypatch.setattr(aact, name, forbidden)


def test_replay_with_snapshot_access_forbidden(monkeypatch):
    forbid_snapshot(monkeypatch)
    ok, reasons = reproduce(SLUG)
    assert ok, reasons
    assert aact_cache.values("study_dates") == {}  # build context is reset


def test_missing_cache_is_rendered_and_never_reads_snapshot(monkeypatch, tmp_path):
    forbid_snapshot(monkeypatch)
    monkeypatch.setattr(aact_cache, "ROOT", tmp_path)
    core = replay_core(SLUG)
    assert core["aact_status"] == "AACT_NOT_MEASURED"
    assert "AACT_NOT_MEASURED</strong>" in render_page(core)
    assert armcontrast.build_arm_index(["NCT04320615"]) == {}


def test_invalid_measurement_is_absent(tmp_path):
    path = tmp_path / "cache" / SLUG / "aact_inputs.json"
    path.parent.mkdir(parents=True)
    original = aact_cache.load(SLUG)
    assert original is not None
    original["values"]["study_dates"] = {"bad": {"completion_date": "invented"}}
    path.write_text(json.dumps(original), encoding="utf-8")
    assert aact_cache.load(SLUG, tmp_path) is None


def test_every_live_topic_has_hashed_measurements():
    root = Path(__file__).resolve().parents[1]
    topics = sorted(p.name for p in (root / "docs" / "reviews").iterdir() if (p / "review.json").is_file())
    for slug in topics:
        doc = aact_cache.load(slug)
        assert doc is not None, slug
        assert set(doc["source_rows"]) == {"studies", "sponsors", "responsible_parties",
                                           "design_groups", "interventions", "design_group_interventions"}
        for rows in doc["source_rows"].values():
            for row in rows:
                assert row["keys"]["nct_id"] in doc["requested_ncts"]
                assert len(row["sha256"]) == 64
