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


def test_plant_a_whole_text_block_needs_a_declared_cc_source():
    body = "Trial results text. " * 400                                     # 8000 chars: full-text sized
    p = "INSTR\n<<<TEXT\n" + body + "\nTEXT>>>\n"
    rec = lambda ref: {"record_id": "mc-blk", "prompt": {"b64": base64.b64encode(p.encode()).decode()},  # noqa: E731
                       "input_digests": [{"ref": ref, "what": "held text shown whole"}]}
    dl = {"10.1/cc": "cc-by", "10.1/bronze": "other-oa"}
    assert rl.text_block_problems(rec("outputs/k_gap/_upw (DOI 10.1/cc)"), dl, {}) == []
    assert rl.text_block_problems(rec("outputs/k_gap/_upw (DOI 10.1/bronze)"), dl, {})
    assert rl.text_block_problems(rec("something undeclared"), dl, {})
    assert rl.text_block_problems(rec("held open text PMID 123 (PMC_OA)"), dl, {"123": "CC"}) == []
    assert rl.text_block_problems(rec("held open text PMID 123 (PMC_OA)"), dl, {"123": "NOT_OPEN"})
    short = {"record_id": "a", "prompt": {"b64": base64.b64encode(b"<<<TEXT\nabstract only\nTEXT>>>").decode()},
             "input_digests": []}
    assert rl.text_block_problems(short, dl, {}) == []                       # abstract-sized: the abstract policy


def test_plant_a_refused_prompt_is_never_sent():
    from reproducible_ai import model_call_live as mcl
    sent = []
    p = ("INSTR\n<<<TEXT\n" + "x " * 4000 + "\nTEXT>>>\n").encode()
    try:
        mcl.call(p, schema={"type": "object"}, model="m", effort="low", caller={"file": "t", "line": "1", "purpose": "t"},
                 input_digests=[{"ref": "undeclared"}], runner=lambda *a, **k: sent.append(1) or {})
        raise AssertionError("not refused")
    except mcl.LicenceRefused:
        pass
    assert not sent


def test_jats_licence_reads_a_creative_commons_licence_named_in_words(tmp_path):
    """False-positive class (6 Oct, 19 refused swap screens): a JATS <permissions> naming the licence in WORDS ('the
    Creative Commons Attribution License (CC BY)') with no creativecommons.org URL is CC; a permissions block with no
    Creative Commons licence stays NOT_OPEN."""
    from reproducible_ai import record_licence as rl
    words = tmp_path / "a.xml"
    words.write_text("<article><permissions><license><license-p>This is an open-access article distributed under the terms "
                     "of the Creative Commons Attribution License (CC BY).</license-p></license></permissions></article>",
                     encoding="utf-8")
    closed = tmp_path / "b.xml"
    closed.write_text("<article><permissions><copyright-statement>All rights reserved.</copyright-statement>"
                      "<license><license-p>For personal use only.</license-p></license></permissions>"
                      "<body>Creative Commons Attribution License (CC BY)</body></article>", encoding="utf-8")
    assert rl.jats_licence(str(words)) == "CC"
    assert rl.jats_licence(str(closed)) == "NOT_OPEN"          # words OUTSIDE <permissions> never count


def test_a_doi_with_parentheses_is_looked_up_whole():
    # 7 Oct: 'DOI 10.1016/s2213-8587(25)00123-4' was cut at the first ')' by [^\s)]+, so its CC BY licence was never
    # found and two open Lancet D&E texts were refused; a ref that WRAPS a DOI in parentheses still drops the closer
    from reproducible_ai import record_licence as rl
    d = "10.1016/s2213-8587(25)00123-4"
    assert rl.ref_licences(f"DOI {d} Unpaywall open text", {}, {d: "cc-by"}) == [(f"DOI {d}", "cc-by")]
    assert rl.ref_licences("trial copy (DOI 10.1/abc)", {}, {"10.1/abc": "cc-by"}) == [("DOI 10.1/abc", "cc-by")]
