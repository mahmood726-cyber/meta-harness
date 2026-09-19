"""Run labels are live UTC inputs; sealed first-run artefacts are historical."""
import datetime
from pathlib import Path

import pytest
from scripts import search_v2_run as live
from scripts import measure_search_v2_measurement as sealed


class FutureClock(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2031, 2, 3, tzinfo=datetime.timezone.utc)


def test_refresh_cli_uses_explicit_current_date(monkeypatch):
    monkeypatch.setattr(live.datetime, "datetime", FutureClock)
    seen = {}
    monkeypatch.setattr(live, "refresh", lambda *a, **kw: seen.update(kw) or 0)
    monkeypatch.setattr(live, "_topics_arg", lambda value: [])
    assert live.main(["refresh", "--label", "r9", "--topics", "all", "--run-date", "2031-02-03"]) == 0
    assert seen["run_date"] == "2031-02-03"


def test_refresh_refuses_stale_date_before_io(monkeypatch):
    monkeypatch.setattr(live.datetime, "datetime", FutureClock)
    monkeypatch.setattr(live, "_split", lambda: pytest.fail("I/O reached before date validation"))
    with pytest.raises(SystemExit, match="UTC"):
        live.refresh("r9", [], "all", "unused", None, ("ctgov",), run_date="2026-09-15")


def test_dated_label_is_not_prefixed_with_first_run_date():
    assert Path(live._candidate_path("2031-02-03r9", "all")).name == "candidates-2031-02-03r9-all.json"
    assert live._snapshot_name("2031-02-03r9").startswith("2031-02-03r9-")


def test_sealed_first_run_refuses_later_clock_before_io(monkeypatch):
    monkeypatch.setattr(sealed.dt, "datetime", FutureClock)
    monkeypatch.setattr(sealed, "_validate_measurement_split", lambda: pytest.fail("sealed run reached I/O on a different date"))
    with pytest.raises(SystemExit, match="sealed"):
        sealed.refresh_measurement()


def test_sealed_artifact_identity_does_not_follow_clock(monkeypatch):
    monkeypatch.setattr(sealed.dt, "datetime", FutureClock)
    assert sealed.FIRST_RUN_DATE in sealed.CANDIDATE_PATH.name
    assert "2031-02-03" not in str(sealed.CANDIDATE_PATH)
