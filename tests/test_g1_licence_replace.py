"""Plant: the licence cache's rename retries a transient Windows sharing denial (WinError 5 killed the 7 Oct dry screen),
and still raises when the denial persists -- a cache write is never silently dropped."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_licence as gl  # noqa: E402


def test_a_transient_denial_is_retried(monkeypatch):
    calls = []

    def flaky(a, b):
        calls.append(1)
        if len(calls) < 3:
            raise PermissionError("WinError 5")
    monkeypatch.setattr(gl.os, "replace", flaky)
    monkeypatch.setattr("time.sleep", lambda s: None)
    gl._replace("a", "b")
    assert len(calls) == 3


def test_a_persistent_denial_raises(monkeypatch):
    def deny(a, b):
        raise PermissionError("WinError 5")
    monkeypatch.setattr(gl.os, "replace", deny)
    monkeypatch.setattr("time.sleep", lambda s: None)
    with pytest.raises(PermissionError):
        gl._replace("a", "b")
