"""Plant: the unit-test limb names EVERY failing test. PR #13's CI refused with '34 failed' and named one: the limb
kept a fixed 15-line tail, and wrapped assertion messages pushed the other 33 names out of it."""
import importlib.util
import os

_P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "verify_all.py")


def _load():
    spec = importlib.util.spec_from_file_location("verify_all_plant", _P)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_failed_line_is_named(monkeypatch):
    va = _load()
    out = "\n".join([f"FAILED tests/test_x.py::test_{i} - AssertionError: long" for i in range(34)]
                    + ["E   wrapped line"] * 40 + ["34 failed, 5734 passed in 772.60s"])
    monkeypatch.setattr(va, "_target", lambda label, paths, refs=(): ("TARGET t", None))
    monkeypatch.setattr(va, "_run", lambda cmd: (1, out))
    state, detail = va.limb_unit_tests()
    assert state == va.REFUSED
    assert all(f"test_x.py::test_{i} " in detail for i in range(34))
    assert detail.rstrip().endswith("34 failed, 5734 passed in 772.60s")
