"""Stale definition-audit rows (external audit 26-A / 28-C / 29): an audit row applies only while the served row is the
version it judged. Before the fix, STRENGTH, REDUCE-IT and FOURIER rows still said "5-point primary" for rows now served
as the 3-point outcomes, and compat_check took the audit row FIRST, so the comparison panel repeated the stale text."""
from __future__ import annotations

import json
from pathlib import Path

from harness import compat_check, defaudit_binding as B, page

ROOT = Path(__file__).resolve().parents[1]


def _trial(**kw):
    t = {"id": "PMID 111", "label": "T", "effect": 0.80, "ci_low": 0.73, "ci_high": 0.88, "scale": "HR",
         "source": "key secondary: CV death, MI or stroke HR 0.80 (0.73-0.88)"}
    t.update(kw)
    return t


def _row(trial, detail="T: 5-point primary (adds unstable angina, revascularization)."):
    return {"detail": detail, "resolution": "DISCLOSED", "judged": {"commit": "abc", **B.trial_fingerprint(trial)}}


def test_PLANT_a_row_judged_on_an_earlier_version_is_not_the_definition():
    old = _trial(effect=0.85, ci_low=0.79, ci_high=0.92, source="primary 5-point HR 0.85 (0.79-0.92)")
    now = _trial()
    audit = {"s::MACE::111": _row(old)}
    assert B.audit_state(audit["s::MACE::111"], now) == B.AUDIT_ROW_STALE
    dims = compat_check.derive_trial_dimensions({"slug": "s"}, {"name": "MACE"}, now, {}, audit)
    assert "5-point primary" not in json.dumps(dims["endpoint_definition"])
    assert dims["definition_audit_row"]["state"] == B.AUDIT_ROW_STALE


def test_a_row_judged_on_the_current_version_still_applies():
    now = _trial()
    audit = {"s::MACE::111": _row(now, detail="T: 3-point key secondary.")}
    dims = compat_check.derive_trial_dimensions({"slug": "s"}, {"name": "MACE"}, now, {}, audit)
    assert "3-point key secondary" in json.dumps(dims["endpoint_definition"]) and "definition_audit_row" not in dims


def test_an_unbound_row_is_never_used():
    now = _trial()
    audit = {"s::MACE::111": {"detail": "T: 5-point primary.", "resolution": "DISCLOSED"}}
    assert B.audit_state(audit["s::MACE::111"], now) == B.UNBOUND
    dims = compat_check.derive_trial_dimensions({"slug": "s"}, {"name": "MACE"}, now, {}, audit)
    assert "5-point primary" not in json.dumps(dims["endpoint_definition"])


def test_PLANT_the_page_table_marks_a_stale_row_as_not_current():
    old = _trial(effect=0.85, source="old")
    r = {"definition_audit": {"s::MACE::111": _row(old)}, "outcomes": [{"name": "MACE", "trials": [_trial()]}]}
    assert "AUDIT_ROW_STALE" in page._definition_audit_block(r) and "not the current definition" in page._definition_audit_block(r)


def test_the_committed_audit_file_is_bound_and_the_named_rows_are_stale_on_the_served_rows():
    da = json.loads((ROOT / "docs" / "definition_audit.json").read_text(encoding="utf-8"))["by_row"]
    assert all("judged" in v for v in da.values()), "run scripts/bind_definition_audit.py"
    states = {}
    for k, row in da.items():
        slug, outcome, pmid = k.split("::", 2)
        r = json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))
        st = page._definition_audit_state(r, outcome, pmid, row)
        if st:
            states[k] = st
    assert len(states) == 19                                          # the rows a served trial reaches today
    for k in ("omega3-cardiovascular-events::Major vascular events / MACE::33190147",          # STRENGTH
              "omega3-cardiovascular-events::Major vascular events / MACE::30415628",          # REDUCE-IT
              "pcsk9-mace::Major adverse cardiovascular events::28304224"):                    # FOURIER
        assert states[k] == B.AUDIT_ROW_STALE, k



def _bind_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("bind_da", ROOT / "scripts" / "bind_definition_audit.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_PLANT_a_recorded_judgment_is_never_overwritten_by_rebinding(monkeypatch):
    """codex pva-defaudit-r1 P1: a later wording edit must not re-bind a row to a newer served version."""
    m = _bind_module()
    recorded = {"commit": "aaaaaaaaaaaa", **B.trial_fingerprint(_trial(effect=0.85))}
    doc = {"by_row": {"topic::MACE::111": {"detail": "edited wording", "resolution": "R", "judged": dict(recorded)}}}
    monkeypatch.setattr(m, "_git", lambda *a: (_ for _ in ()).throw(AssertionError("history must not be read")))
    assert m.bound(doc)["by_row"]["topic::MACE::111"]["judged"] == recorded


def test_PLANT_a_git_failure_is_not_read_as_an_absent_trial(monkeypatch):
    """codex pva-defaudit-r1 P2: only a missing review path is NOT_FOUND; any other git failure raises."""
    import subprocess
    import pytest
    m = _bind_module()
    doc = {"by_row": {"topic::MACE::111": {"detail": "d", "resolution": "R"}}}

    def fake(*a):
        if a[0] == "log":
            return b"a" * 40
        if a[0] == "show" and a[1].endswith("definition_audit.json"):
            return json.dumps({"by_row": {"topic::MACE::111": {"detail": "d", "resolution": "R"}}}).encode()
        raise subprocess.CalledProcessError(128, ["git", *a])
    monkeypatch.setattr(m, "_git", fake)
    with pytest.raises(subprocess.CalledProcessError):
        m.bound(doc)


def test_PLANT_a_non_dict_judgment_is_unbound_and_disclosed_without_crashing():
    """codex pva-defaudit-r2 P2."""
    now = _trial()
    audit = {"s::MACE::111": {"detail": "T: 5-point primary.", "resolution": "R", "judged": "legacy"}}
    dims = compat_check.derive_trial_dimensions({"slug": "s"}, {"name": "MACE"}, now, {}, audit)
    assert dims["definition_audit_row"]["state"] == B.UNBOUND and dims["definition_audit_row"]["judged_commit"] is None
    r = {"definition_audit": audit, "outcomes": [{"name": "MACE", "trials": [now]}]}
    assert "UNBOUND" in page._definition_audit_block(r)
