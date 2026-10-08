"""D8 over every TRACKED recorded call (8 Oct audit: 12 acquisition records carried full text of CC BY-NC or unlicensed
articles -- ODYSSEY FH I/II, TRANSFORM-1, PARALLEL-HF -- and were quarantined). A recorded prompt is a committed, public
record, so any full-text block it carries must come from an article whose Europe PMC licence is CC BY / CC0
(scripts/g1_licence.py). Offline: the licence must already be cached; an uncached licence is closed and fails here, so a
new record cannot be committed before its article's licence has been read."""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_licence as gl  # noqa: E402
from reproducible_ai import record_licence as rl  # noqa: E402


def full_text_blocks(rec):
    """[(pmid, chars, how)] of every full-text block a record's prompt carries."""
    p = rl._prompt_text(rec)
    out = []
    i = p.find("=== EVIDENCE ===")
    if i >= 0:
        try:
            ev = json.loads(p[i + len("=== EVIDENCE ==="):])
        except ValueError:
            ev = None
        pm = ev.get("pmid") if isinstance(ev, dict) else None
        for d in rl._walk(ev):
            t = d.get("text")
            if isinstance(t, str) and len(t) > rl.MIN_TEXT and (d.get("pmid") or d.get("doi")):
                out.append((str(d.get("pmid") or pm or ""), len(t), "evidence full_text"))
    out += [(str(a), b, c) for a, b, c in rl.embedded_sources(rec)]
    return out


def test_the_audit_finds_a_planted_non_cc_by_block(monkeypatch):
    import base64
    ev = {"pmid": "26330422", "full_text": {"pmid": "26330422", "text": "x" * 3000}}
    p = "I\n\n=== EVIDENCE ===\n" + json.dumps(ev)
    rec = {"record_id": "plant", "prompt": {"b64": base64.b64encode(p.encode()).decode()}, "input_digests": []}
    assert ("26330422", 3000, "evidence full_text") in full_text_blocks(rec)
    monkeypatch.setattr(gl, "licence", lambda pmid, offline=False: {"license": "cc by-nc", "open": False})
    assert not gl.licence("26330422", offline=True)["open"]


def test_no_tracked_record_carries_full_text_of_an_article_that_is_not_cc_by_or_cc0():
    files = subprocess.run(["git", "ls-files", "registry/model_calls/mc-*.json"], cwd=ROOT, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL).stdout.split()
    bad = []
    for f in files:
        rec = json.load(open(os.path.join(ROOT, f), encoding="utf-8"))
        for pmid, chars, how in full_text_blocks(rec):
            v = gl.licence(pmid, offline=True) if pmid else {"open": False, "license": None}
            if not v.get("open"):
                bad.append(f"{f}: {chars} chars of PMID {pmid} ({how}); article licence {v.get('license')!r} "
                           f"({v.get('state', 'cached')})")
    assert not bad, "\n".join(bad[:20])
