"""A run ledger entry that says RAN_OK must point at a model-call record that is in the tree: a replay of a record that
history removed (non-open text or private paths; the 5 Oct rewrite) crashes the regeneration, and a union merge of two
lanes' ledgers re-introduced such entries once. Quarantined entries keep their record_id with the reason."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC_DIRS = [os.path.join(ROOT, "evidence", "model_calls"), os.path.join(ROOT, "registry", "model_calls")]


def _present():
    out = set()
    for d in REC_DIRS:
        for f in glob.glob(os.path.join(d, "**", "mc-*.json"), recursive=True):
            out.add(os.path.basename(f)[:-5])
    return out


def test_every_ran_ok_run_points_at_a_record_in_the_tree():
    have = _present()
    bad = []
    for f in glob.glob(os.path.join(ROOT, "registry", "secondary_meta", "runs", "*.json")):
        for k, v in json.load(open(f, encoding="utf-8")).items():
            if isinstance(v, dict) and v.get("state") == "RAN_OK" and v.get("record_id") and v["record_id"] not in have:
                bad.append(f"{os.path.basename(f)}::{k} -> {v['record_id']}")
    assert not bad, "RAN_OK entries point at records not in the tree:\n" + "\n".join(bad)
