"""D8 on main (captain, 8 Oct): two recorded acquisition calls carried 34819 chars of PMID 26330422 full text (ODYSSEY
FH I/II), whose Europe PMC licence is 'cc by-nc' -- not CC BY / CC0. k-gap quarantined them on acq/k-gap (1162f4121);
these plants keep them out of main, and keep every acquisition-ledger reference to a recorded call resolvable."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINED = ("mc-2249c745cf51bbc0c6e38108a0d3c108", "mc-3c1d4445e0c6a23176402a4320e16ffd")


def _refs(o):
    if isinstance(o, dict):
        if isinstance(o.get("record_id"), str):
            yield o
        for v in o.values():
            yield from _refs(v)
    elif isinstance(o, list):
        for v in o:
            yield from _refs(v)


def test_PLANT_the_non_cc_by_records_are_not_on_main():
    for rid in QUARANTINED:
        assert not os.path.exists(os.path.join(ROOT, "registry", "model_calls", rid + ".json")), rid


def test_PLANT_no_ledger_points_at_a_quarantined_record_and_each_is_marked():
    paths = glob.glob(os.path.join(ROOT, "registry", "g1_acquired", "*.json")) + [
        os.path.join(ROOT, "registry", "model_proposals", "g1_trial_acquire.json")]
    marked = 0
    for p in paths:
        d = json.load(open(p, encoding="utf-8"))
        for r in _refs(d):
            assert r["record_id"] not in QUARANTINED, (p, r["record_id"])
        text = json.dumps(d)
        marked += sum(text.count(f'"quarantined_record": "{rid}"') for rid in QUARANTINED)
    assert marked == 4, marked     # 2 acquisition rows (pcsk9-mace) + 2 proposal runs


def test_every_acquisition_row_record_id_resolves_to_a_committed_record():
    for p in glob.glob(os.path.join(ROOT, "registry", "g1_acquired", "*.json")):
        for r in _refs(json.load(open(p, encoding="utf-8"))):
            assert os.path.exists(os.path.join(ROOT, "registry", "model_calls", r["record_id"] + ".json")), (p, r["record_id"])
