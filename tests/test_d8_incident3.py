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


def test_no_old_id_survives_outside_the_audit_trail():
    olds = [r["old"] for r in _incident()["records"]]
    args = [a for o in olds for a in ("-e", o)]
    out = subprocess.run(["git", "grep", "-l", *args], cwd=ROOT, capture_output=True, text=True).stdout.split()
    news = {r["new"] for r in _incident()["records"]}
    allowed = {"registry/d8_incidents.json", "scripts/d8_redact_incident3.py", "tests/test_d8_incident3.py",
               "tests/test_record_licence.py"}                               # a docstring naming the incident
    extra = [p for p in out if p not in allowed and os.path.basename(p)[:-5] not in news]
    assert not extra, extra


def test_a_read_resting_on_a_redacted_record_no_longer_upgrades_the_row():
    news = {r["new"] for r in _incident()["records"]}
    reads = json.load(open(os.path.join(ROOT, "registry", "provenance_recorded_reads.json"), encoding="utf-8"))["reads"]
    hit = [r for r in reads.values() if r.get("record_id") in news]
    assert hit and all(r["state"] == "WITHDRAWN_D8_3" and "NOT CC BY / CC0" in r["shown"] for r in hit)
