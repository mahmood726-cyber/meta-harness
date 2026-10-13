"""D8 incident #3 (Mahmood, 13 Oct: named incident + redact going forward). The ledger names every redacted record and
each source's licence; every redacted record withholds its prompt bytes but keeps the hash; no old id survives outside the
audit trail; and a read resting on a redacted record no longer upgrades a served row. The class itself is pinned by
tests/test_record_licence.py::test_no_tracked_record_carries_text_from_a_copy_not_marked_open (red on these 33 before)."""
import json
import os
import subprocess

from reproducible_ai import model_source as ms
from reproducible_ai import record_licence as rl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "registry", "d8_incidents.json")


def _incident():
    d = json.load(open(LEDGER, encoding="utf-8"))
    return [i for i in d["incidents"] if i["id"] == "D8-3"][0]


def _redacted_in_store():
    out = {}
    for f in rl.tracked_records():
        r = json.load(open(f, encoding="utf-8"))
        if r.get("d8_redaction"):
            out[r["record_id"]] = r
    return out


def test_ledger_and_store_name_the_same_records():
    recs = _incident()["records"]
    assert len(recs) == len({r["old"] for r in recs}) == 33
    assert {r["new"] for r in recs} == set(_redacted_in_store())


def test_every_source_named_is_outside_cc_by_and_cc0():
    for r in _incident()["records"]:
        assert r["sources"], r["old"]
        for s in r["sources"]:
            assert not rl._is_open(s["guard_licence"]), (r["old"], s)


def test_every_redacted_record_withholds_the_prompt_and_keeps_its_hash():
    store = _redacted_in_store()
    for r in _incident()["records"]:
        rec = store[r["new"]]
        assert rec["prompt"]["b64"] is None and rec["prompt"]["sha256"] == r["prompt_sha256"]
        assert rec["prompt"]["bytes"] == r["prompt_bytes"]
        assert rec["record_id"] == ms.record_id_of(rec)                    # re-identified, not edited in place
        assert rec["d8_redaction"]["original_record_id"] == r["old"]
        assert ms.record_problems(rec) == ["prompt: no stored bytes (the stored prompt is lost -- this record cannot replay)"]


def _grep_ids(ids):
    """Files naming any of `ids`. git grep exits 1 for none; any other failure RAISES -- a search that did not run is
    never 'no surviving id' (codex d8x-cap-r2 #3)."""
    p = subprocess.run(["git", "grep", "-l", *[a for i in ids for a in ("-e", i)]], cwd=ROOT, capture_output=True,
                       text=True)
    if p.returncode not in (0, 1):
        raise RuntimeError(f"git grep failed ({p.returncode}): {p.stderr.strip()[:200]}")
    return p.stdout.split()


def test_no_old_id_survives_outside_the_audit_trail():
    olds = [r["old"] for r in _incident()["records"]]
    out = _grep_ids(olds)
    news = {r["new"] for r in _incident()["records"]}
    allowed = {"registry/d8_incidents.json", "scripts/d8_redact_incident3.py", "tests/test_d8_incident3.py",
               "tests/test_record_licence.py"}                               # a docstring naming the incident
    extra = [p for p in out if p not in allowed and os.path.basename(p)[:-5] not in news]
    assert not extra, extra


def test_a_read_resting_on_a_redacted_record_no_longer_upgrades_the_row():
    news = {r["new"] for r in _incident()["records"]}
    reads = json.load(open(os.path.join(ROOT, "registry", "provenance_recorded_reads.json"), encoding="utf-8"))["reads"]
    hit = [r for r in reads.values() if r.get("record_id") in news]
    # a read still resting on a redacted record is withdrawn; omega3 21115589 was then RE-READ from its open abstract
    # (mc-46a94e46, 'abstract only; held copy not CC: CC_RESTRICTED') and that read replaced it
    assert all(r["state"] == "WITHDRAWN_D8_3" and "NOT CC BY / CC0" in r["shown"] for r in hit)
    o = reads["omega3-cardiovascular-events|21115589|Major vascular events / MACE"]
    assert o["record_id"] not in news and o["shown"].startswith("trial report PMID 21115589 (abstract only")


def test_plant_a_failing_git_query_is_an_error_not_an_empty_answer(monkeypatch):
    """codex d8x-cap-r1 #1: _tracked / _refs read a git failure (exit 128) as 'no record' / 'no reference' -- a failed
    reference search would let redact() delete a record and leave every reference dangling."""
    import importlib
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "scripts"))
    d8 = importlib.import_module("d8_redact_incident3")

    class _P:
        returncode, stdout, stderr = 128, "", "fatal: not a git repository"
    monkeypatch.setattr(d8.subprocess, "run", lambda *a, **k: _P())
    import pytest
    for fn in (d8._tracked, d8._refs):
        with pytest.raises(RuntimeError):
            fn("mc-x")


def test_plant_a_later_batch_keeps_the_earlier_records(tmp_path, monkeypatch):
    """codex d8x-cap-r1 #2: a second run that redacts more records replaced the ledger's list, losing the audit
    mapping (and the reads to withdraw) of the first batch."""
    import importlib
    import sys as _s
    _s.path.insert(0, os.path.join(ROOT, "scripts"))
    d8 = importlib.import_module("d8_redact_incident3")
    led = tmp_path / "l.json"
    led.write_text(json.dumps({"incidents": [{"id": "D8-3", "records": [{"old": "mc-a", "new": "mc-b"}]}]}), "utf-8")
    monkeypatch.setattr(d8, "LEDGER", str(led))
    monkeypatch.setattr(d8, "incident_class", lambda: {"mc-c": []})
    monkeypatch.setattr(d8, "redact", lambda o, v: {"old": o, "new": "mc-d", "sources": v})
    seen = {}
    monkeypatch.setattr(d8, "withdraw_reads", lambda news: seen.setdefault("news", set(news)) and 0)
    monkeypatch.setattr(d8.subprocess, "run", lambda *a, **k: None)
    d8.main()
    recs = json.loads(led.read_text("utf-8"))["incidents"][0]["records"]
    assert {r["old"] for r in recs} == {"mc-a", "mc-c"} and seen["news"] == {"mc-b", "mc-d"}


def test_plant_references_are_found_before_the_original_is_removed(monkeypatch, tmp_path):
    """codex d8x-cap-r2 #2: redact() removed the original record, THEN searched for references -- a failing search left
    the references dangling and the ledger without the mapping. The search now runs first; on failure nothing moves."""
    import importlib
    import sys as _s
    import pytest
    _s.path.insert(0, os.path.join(ROOT, "scripts"))
    d8 = importlib.import_module("d8_redact_incident3")
    rec_path = tmp_path / "mc-old.json"
    rec_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(d8, "ROOT", str(tmp_path))
    monkeypatch.setattr(d8, "_tracked", lambda name: ["mc-old.json"])
    monkeypatch.setattr(d8.ms, "load_record", lambda p: {"record_id": "mc-old", "prompt": {"sha256": "s", "bytes": 1},
                                                         "response": {"b64": ""}})
    monkeypatch.setattr(d8.ms, "record_id_of", lambda r: "mc-new")
    monkeypatch.setattr(d8.ms, "record_problems", lambda r: ["prompt: no stored bytes"])
    monkeypatch.setattr(d8, "_refs", lambda old: (_ for _ in ()).throw(RuntimeError("git grep failed")))
    with pytest.raises(RuntimeError):
        d8.redact("mc-old", [])
    assert rec_path.exists() and not (tmp_path / "mc-new.json").exists()


def test_plant_the_audit_search_must_run_to_count_as_clean(monkeypatch):
    """codex d8x-cap-r2 #3: test_no_old_id_survives_outside_the_audit_trail read a failing git grep (exit 128) as 'no
    surviving id'. The helper it now uses raises unless git answered (0 found, 1 none)."""
    import pytest

    class _P:
        returncode, stdout, stderr = 128, "", "fatal"
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: _P())
    with pytest.raises(RuntimeError):
        _grep_ids(["mc-x"])
