"""The review runner's reply parser (coverage lane, 12 Oct): agy answers {"defects": [...]} and the runner read only a
'findings' key, so 18 agy defects across 5 runs (p0-r1, p0-r5, pr53-cap-r1..r3) were recorded as NO FINDINGS. A reply is
never read as empty unless it says so in a key the runner knows; anything else is kept whole as UNSTRUCTURED."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import pr_codex_review as R  # noqa: E402

D = {"severity": "P0", "file": "a.py", "function": "f", "claim": "c", "failing_input": "i", "expected": "e", "actual": "x"}


def test_a_defects_key_is_read():
    assert [f["claim"] for f in R.parse_reply('{"defects": [%s]}' % __import__("json").dumps(D))] == ["c"]


def test_a_fenced_defects_key_is_read():
    assert len(R.parse_reply('```json\n{"defects": [{"claim": "c"}, {"claim": "d"}]}\n```')) == 2


def test_an_unknown_shape_is_unstructured_never_empty():
    out = R.parse_reply('{"verdict": "looks fine", "notes": ["x"]}')
    assert len(out) == 1 and out[0]["severity"] == "UNSTRUCTURED"


def test_an_explicit_empty_findings_list_is_empty():
    assert R.parse_reply('{"findings": []}') == [] and R.parse_reply('{"defects": []}') == [] and R.parse_reply("[]") == []


def test_a_second_json_object_keeps_the_reply_whole():
    out = R.parse_reply('{"defects": [{"claim": "c"}]}\n{"summary": "x"}')
    assert len(out) >= 1 and (out[0]["claim"] == "c" or out[0]["severity"] == "UNSTRUCTURED")


def test_a_later_runner_never_drops_an_earlier_runners_entry(tmp_path, monkeypatch):
    """m2comb-cap-r2 (12 Oct): two runners loaded the proposals file at start; the later write dropped the other's run."""
    import json
    p = tmp_path / "prop.json"
    monkeypatch.setattr(R, "PROP", str(p))
    p.write_text(json.dumps({"old": {"runs": {}}}), encoding="utf-8")
    snapshot_a = json.loads(p.read_text(encoding="utf-8"))           # runner A loads
    snapshot_b = json.loads(p.read_text(encoding="utf-8"))           # runner B loads
    snapshot_a["a-run"] = {"runs": {"g1": 1}}
    R.write_entries(snapshot_a, "a-run")
    snapshot_b["b-run"] = {"runs": {"g1": 2}}
    R.write_entries(snapshot_b, "b-run")
    assert set(json.loads(p.read_text(encoding="utf-8"))) == {"old", "a-run", "b-run"}


def test_plant_a_test_or_registry_only_pr_is_reviewed_when_asked(monkeypatch):
    """#97 / #98 (13 Oct) changed only tests/ and registry/: the code-only filter gave 0 groups, so the PR had no
    review at all. --dirs adds those prefixes (and .json / .md there); without it the default is unchanged."""
    import pr_codex_review as r
    names = "tests/test_regex_freeze.py\nregistry/regex_freeze.json\ndocs/harness/x.py\nharness/a.py\n"
    monkeypatch.setattr(r, "_git", lambda *a: names if "--name-only" in a else f"+diff of {a[-1]}\n")
    assert [f for _, g in r.groups("b", "h") for f, _ in g] == ["harness/a.py"]
    got = [f for _, g in r.groups("b", "h", ("tests/", "registry/")) for f, _ in g]
    assert got == ["tests/test_regex_freeze.py", "registry/regex_freeze.json", "harness/a.py"]


def test_plant_an_agy_call_is_licence_checked_first(monkeypatch, tmp_path):
    """mcl.agy_call has no licence guard (mcl.call has one at call time): the runner checks the exact prompt with the
    shared D8 guard and refuses the call on any problem -- agy is never reached."""
    import pr_codex_review as r
    monkeypatch.setattr(r, "groups", lambda *a, **k: [("g1", [("harness/a.py", "+x\n")])])
    monkeypatch.setattr(r.record_licence, "record_problems", lambda rec, *a, **k: ["carries NC text"])
    monkeypatch.setattr(r.mcl, "agy_call", lambda *a, **k: (_ for _ in ()).throw(AssertionError("agy was called")))
    monkeypatch.setattr(r, "PROP", str(tmp_path / "p.json"))
    with pytest.raises(SystemExit, match="D8: refusing an agy call"):
        r.main(["--run", "--reader", "agy", "--name", "t", "--base", "b", "--head", "h"])


def test_plant_an_agy_group_fits_one_windows_command_line(monkeypatch):
    """agy takes its prompt as the --print ARGUMENT (no stdin in text mode): a 60,000-char group raised WinError 206
    'filename or extension is too long' and pr99-cap-r1-agy reviewed nothing (13 Oct). agy groups are capped, and a file
    diff over the cap is split at line boundaries into numbered parts -- every line is still read, none truncated."""
    import pr_codex_review as r
    big = "".join(f"+line {i} " + "x" * 80 + "\n" for i in range(700))          # ~62,000 chars, one file
    monkeypatch.setattr(r, "_git", lambda *a: "harness/a.py\n" if "--name-only" in a else big)
    gs = r.groups("b", "h", (), limit=r.AGY_GROUP_CHARS)
    parts = [d for _, g in gs for _, d in g]
    assert all(len(d) <= r.AGY_GROUP_CHARS for d in parts) and len(parts) >= 3
    assert "".join(parts) == big                                               # nothing dropped, nothing truncated
    assert r.AGY_GROUP_CHARS + 8000 < 32767                                    # room for the preface and instructions
