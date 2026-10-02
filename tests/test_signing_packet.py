"""The signing packet and its guard (scripts/signing_packet.py), planted with the cases that have actually happened.

MAIN-14 (packet v1, 2026-09-29): spironolactone was presented with a "notice sha256" computed over a record the
packet generator built by hand -- there was no derived notice. main's 65acd80 says packet_guard.py was planted with
that case and refused it; the script was never committed. This file is its replacement's proof.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, str(ROOT / "scripts" / f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sp = _load("signing_packet")


def _open_notices():
    return [n for n in sp._notices(ROOT) if not sp._signed(n)]


pytestmark = pytest.mark.skipif(not _open_notices(), reason="no OPEN notice in this tree to build a packet from")


def _rewrite(path: Path, text: str):
    path.write_bytes(text.encode("utf-8"))
    Path(str(path) + ".sha256").write_text(f"{hashlib.sha256(text.encode('utf-8')).hexdigest()} *{path.name}\n",
                                           encoding="utf-8")


@pytest.fixture
def packet(tmp_path):
    out = tmp_path / "PACKET.md"
    sp.build(ROOT, "test packet", out, "base: test")
    return out


def test_a_built_packet_passes_its_guard_and_splits_by_the_tools_annotation(packet):
    assert sp.guard(ROOT, packet) == []
    text = packet.read_text(encoding="utf-8")
    a, b = text.split("## B. ")
    for n in _open_notices():
        _, sha, ann = sp.block_and_sha(ROOT, n)
        assert sha in (b if ann.get("conclusion_changed") else a), (n["slug"], n["outcome"])


def test_PLANT_MAIN14_an_entry_with_no_derived_notice_is_refused(packet):
    text = packet.read_text(encoding="utf-8")
    fake = ("### V3-99 — spironolactone-hfref-mortality / Hospitalisation that has no notice\n\n"
            "`rendered_sha256 " + "0" * 64 + "`\n\nA hand-built record.\n\n")
    _rewrite(packet, text.replace("## B. ", fake + "## B. ", 1))
    problems = sp.guard(ROOT, packet)
    assert any("NO DERIVED NOTICE" in p and "V3-99" in p for p in problems), problems


def test_PLANT_a_changed_number_in_a_block_is_refused(packet):
    text = packet.read_text(encoding="utf-8")
    m = re.search(r"Now: k = (\d+), (\d+\.\d\d)", text)
    assert m, "no 'Now:' figure in the packet to tamper with"
    _rewrite(packet, text.replace(m.group(0), f"Now: k = {m.group(1)}, 9.99", 1))
    assert any("block text differs" in p for p in sp.guard(ROOT, packet))


def test_PLANT_a_withdrawn_conclusion_in_the_batch_section_is_refused(packet):
    text = packet.read_text(encoding="utf-8")
    head, b = text.split("## B. ", 1)
    entries = re.split(r"(?=^### )", b, flags=re.M)
    individual = [e for e in entries if e.startswith("### ")]
    if not individual:
        pytest.skip("no conclusion-changing notice is open in this tree")
    moved = individual[0].split("```")[0]          # the entry without its own signature line
    _rewrite(packet, head.replace("## A. ", "## A. ", 1).rstrip() + "\n\n" + moved + "## B. " + b.replace(individual[0], ""))
    assert any("must be INDIVIDUAL" in p for p in sp.guard(ROOT, packet))


def test_PLANT_a_signed_notice_cannot_be_re_presented(packet):
    signed = next(n for n in sp._notices(ROOT) if sp._signed(n))
    block, sha, _ = sp.block_and_sha(ROOT, signed)
    text = packet.read_text(encoding="utf-8")
    entry = (f"### V3-98 — {signed['slug']} / {signed['outcome']}\n\n`rendered_sha256 {sha}`\n\n"
             f"{sp.visible_text(block)}\n\n")
    _rewrite(packet, text.replace("## B. ", entry + "## B. ", 1))
    assert any("V3-98" in p and "already" in p for p in sp.guard(ROOT, packet))


def test_PLANT_a_packet_whose_digest_file_is_stale_is_refused(packet):
    packet.write_bytes(packet.read_bytes() + b"\n")
    assert any(".sha256 does not match" in p for p in sp.guard(ROOT, packet))


def test_countersign_acts_on_the_open_notice_when_a_signed_one_shares_the_outcome(tmp_path, monkeypatch):
    cs = _load("countersign_result_change")
    signed = {"slug": "t", "outcome": "O", "reviewer_countersignature": {"state": "BATCH_SEEN_AND_SIGNED"}}
    opened = {"slug": "t", "outcome": "O", "reviewer_countersignature": {"state": "OPEN"}}
    p = tmp_path / "rc.json"
    p.write_text(json.dumps({"notices": [signed, opened]}), encoding="utf-8")
    monkeypatch.setattr(cs, "PATH", p)
    _, n = cs._notice("t", "O")
    assert n["reviewer_countersignature"]["state"] == "OPEN"
    p.write_text(json.dumps({"notices": [signed]}), encoding="utf-8")
    with pytest.raises(SystemExit):
        cs._notice("t", "O")                       # nothing open: refuse rather than re-sign a signed notice
