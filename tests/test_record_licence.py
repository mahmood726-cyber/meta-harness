"""A committed model-call record's prompt may carry source text only from a copy marked open (reproducible_ai/
record_licence.py). Incident 5 Oct: mc-dcb6796c carried SMART's author-manuscript text (24,886 bytes) into the public repo.
Every tracked record is checked; the existing debt is listed by id in registry/record_licence_exceptions.json (it may only
shrink); a new violation fails the unit-test limb, so the pre-commit hook and CI refuse it."""
import base64
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import record_licence as rl  # noqa: E402

EXC = os.path.join(ROOT, "registry", "record_licence_exceptions.json")


def _record(pmid, text, rid="mc-plant"):
    ev = {"trial": "SMART", "full_text": {"pmid": pmid, "sha256": "x", "chars": len(text), "text": text}}
    p = "INSTRUCTIONS\n\n=== EVIDENCE ===\n" + json.dumps(ev)
    return {"record_id": rid, "prompt": {"b64": base64.b64encode(p.encode()).decode(), "bytes": len(p), "sha256": "x"},
            "input_digests": [{"ref": "evidence"}]}


def test_plant_a_prompt_with_non_open_text_is_refused():
    body = "In-hospital death before 30 days. " * 100
    lic = {"29485925": "PMC_AUTHOR_MANUSCRIPT", "28701470": "CC"}
    assert rl.record_problems(_record("29485925", body), lic)                  # author manuscript: refused
    assert rl.record_problems(_record("99999999", body), lic)                  # unknown licence: refused
    assert rl.record_problems(_record("28701470", body), lic) == []           # CC: fine
    assert rl.record_problems(_record("29485925", "short label"), lic) == []  # no source text carried


def test_plant_a_declared_full_text_prompt_is_checked_and_an_abstract_is_not():
    long_p = "x" * 7000
    r = {"record_id": "mc-d", "prompt": {"b64": base64.b64encode(long_p.encode()).decode()},
         "input_digests": [{"ref": "PMID 30541065 record + PMC OA full text (first 60000 chars)"}]}
    assert rl.record_problems(r, {"30541065": "NOT_OPEN"})
    short = dict(r, prompt={"b64": base64.b64encode(b"abstract only").decode()})
    assert rl.record_problems(short, {"30541065": "NOT_OPEN"}) == []


def test_no_tracked_record_carries_text_from_a_copy_not_marked_open():
    listed = (json.load(open(EXC, encoding="utf-8")).get("records") or {}) if os.path.exists(EXC) else {}
    lic = rl.licences()
    bad, seen = [], set()
    for f in rl.tracked_records():
        r = json.load(open(f, encoding="utf-8"))
        probs = rl.record_problems(r, lic)
        if probs:
            seen.add(r.get("record_id"))
            if r.get("record_id") not in listed:
                bad += probs
    assert not bad, "model-call records carry text from a copy not marked open:\n" + "\n".join(bad)
    # the list may only shrink: an entry that no longer fails must be removed
    stale = sorted(set(listed) - seen)
    assert not stale, f"registry/record_licence_exceptions.json lists records that no longer fail: {stale}"
