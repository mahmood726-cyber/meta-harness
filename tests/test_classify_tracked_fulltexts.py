"""V13-04Q: only CC BY / CC0 texts may stay tracked; every other licence, and an unknown one, is a removal candidate."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s = importlib.util.spec_from_file_location("ctf", os.path.join(ROOT, "scripts", "classify_tracked_fulltexts.py"))
ctf = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ctf)


def test_PLANT_only_cc_by_and_cc0_are_kept():
    assert ctf.verdict("cc by") == ctf.verdict("CC0") == "KEEP_CC"
    for lic in ("cc by-nc", "cc by-nc-nd", "cc by-nd", "cc by-sa", "cc by-nc-sa", "all rights reserved"):
        assert ctf.verdict(lic) == "NOT_CC", lic
    assert ctf.verdict(None) == ctf.verdict("") == "UNKNOWN"


def test_the_committed_ledger_covers_every_tracked_fulltext():
    import json
    d = json.load(open(os.path.join(ROOT, "registry", "tracked_fulltext_licences.json"), encoding="utf-8"))
    led = {r["file"] for r in d["rows"]}
    tracked = {r["file"] for r in ctf.tracked_fulltexts()}
    assert tracked <= led, sorted(tracked - led)[:5]
