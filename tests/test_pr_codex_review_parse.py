"""The review runner's reply parser (coverage lane, 12 Oct): agy answers {"defects": [...]} and the runner read only a
'findings' key, so 18 agy defects across 5 runs (p0-r1, p0-r5, pr53-cap-r1..r3) were recorded as NO FINDINGS. A reply is
never read as empty unless it says so in a key the runner knows; anything else is kept whole as UNSTRUCTURED."""
import os
import sys

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
