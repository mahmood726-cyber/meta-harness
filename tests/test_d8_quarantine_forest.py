"""D8 (forest lane, 8 Oct): two of this lane's acquisition reruns (pcsk9 ODYSSEY FH I / FH II) carried the same 34819
chars of PMID 26330422 full text the captain quarantined on main (4e56ed2fd): Europe PMC 'cc by-nc', not CC BY / CC0.
Removed at the tip; these plants keep them out and keep the ledger marking them."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUARANTINED = ("mc-693c091da24e2063ee283f2903f7bd42", "mc-83bf1a20c689a40e435baa4f0e59484d")
# the class audit of every recorded prompt (g1_licence.py rule, CC BY / CC0 only) found 5 more of this lane's
# acquisition calls carrying CC BY-NC / CC BY-NC-ND full text; 2 are no longer referenced by any ledger
AUDIT = ("mc-001f70b7e43529417fb9340ae872e611", "mc-b174f91cf8d5d9d98dd46d2df0c89824", "mc-cf73b349406ad3fa3955bcff09b4c758",
         "mc-d1c9a953bbafe2f80a071e17e6a5c7ed", "mc-e7532b8878412f6ed6b13414877c0577")


def test_PLANT_the_audit_quarantined_records_are_not_in_the_tree_and_no_ledger_points_at_them():
    import glob
    for rid in AUDIT:
        assert not os.path.exists(os.path.join(ROOT, "registry", "model_calls", rid + ".json")), rid
    for p in glob.glob(os.path.join(ROOT, "registry", "g1_acquired", "*.json")) + [
            os.path.join(ROOT, "registry", "model_proposals", "g1_trial_acquire.json")]:
        t = open(p, encoding="utf-8").read()
        for rid in AUDIT:
            assert f'"record_id": "{rid}"' not in t, (p, rid)


def test_PLANT_the_forest_lane_cc_by_nc_records_are_not_in_the_tree():
    for rid in QUARANTINED:
        assert not os.path.exists(os.path.join(ROOT, "registry", "model_calls", rid + ".json")), rid


def test_PLANT_the_ledger_marks_them_and_never_points_at_them():
    t = open(os.path.join(ROOT, "registry", "model_proposals", "g1_trial_acquire.json"), encoding="utf-8").read()
    for rid in QUARANTINED:
        assert f'"record_id": "{rid}"' not in t and f'"quarantined_record": "{rid}"' in t
