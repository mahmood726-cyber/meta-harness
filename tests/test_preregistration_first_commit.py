"""A prospective-registration claim needs the protocol's FIRST commit to be protocol-only. A later protocol-only commit -- an
amendment, such as V13-03Q's dated post-hoc estimand amendment -- can never show the protocol preceded synthesis.
preregistration_sha used to walk every protocol commit and return the first non-build one, so the V13 amendment commit was
reported as 'prospective: True' for topics whose protocol first entered inside a build (denosumab, sglt2-ckd)."""
from harness import registration as reg


def _fake(monkeypatch, log_oldest_first, builds, batch=None, prereg_text=""):
    monkeypatch.setattr(reg, "_log_all", lambda path: list(reversed(log_oldest_first)))
    monkeypatch.setattr(reg, "is_build_commit", lambda sha: sha in builds)
    monkeypatch.setattr(reg, "_git_log", lambda path: (batch if path == reg.PREREG else log_oldest_first[-1]))
    monkeypatch.setattr(reg, "_batch_precedes", lambda batch_sha, first_sha: batch_sha == "batch_early")
    import builtins, io
    real_open = builtins.open
    monkeypatch.setattr(builtins, "open", lambda p, *a, **k: io.StringIO(prereg_text) if str(p).endswith(reg.PREREG) else real_open(p, *a, **k))


def test_PLANT_a_later_protocol_only_amendment_is_not_a_prospective_registration(monkeypatch):
    _fake(monkeypatch, ["build1", "amend2"], builds={"build1"})
    r = reg.preregistration_sha("t")
    assert r["prospective"] is False and r["sha"] is None, r


def test_a_protocol_whose_first_commit_is_protocol_only_is_prospective(monkeypatch):
    _fake(monkeypatch, ["prot1", "build2", "amend3"], builds={"build2"})
    r = reg.preregistration_sha("t")
    assert r["prospective"] is True and r["sha"] == "prot1"


def test_the_batch_counts_only_when_it_precedes_the_first_protocol_commit(monkeypatch):
    _fake(monkeypatch, ["build1"], builds={"build1"}, batch="batch_early", prereg_text="t")
    assert reg.preregistration_sha("t")["prospective"] is True
    _fake(monkeypatch, ["build1"], builds={"build1"}, batch="batch_late", prereg_text="t")
    assert reg.preregistration_sha("t")["prospective"] is False


def test_PLANT_a_git_failure_is_not_reported_as_non_ancestry(monkeypatch):
    """codex v13-apply-r2 P2: an ancestry check that could not run must not return a verdict."""
    import subprocess
    import pytest

    def boom(*a, **k):
        raise FileNotFoundError("git unavailable")
    monkeypatch.setattr(reg.subprocess, "run", boom)
    with pytest.raises(RuntimeError):
        reg._batch_precedes("a" * 40, "b" * 40)
    monkeypatch.setattr(reg.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 128, b"", b"fatal: bad object"))
    with pytest.raises(RuntimeError):
        reg._batch_precedes("a" * 40, "b" * 40)
    monkeypatch.setattr(reg.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, b"", b""))
    assert reg._batch_precedes("a" * 40, "b" * 40) is False
