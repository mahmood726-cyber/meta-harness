"""Plant (5 Oct night, forest lane; the consolidation's invariant): no run-ledger entry is RAN_OK without its record in
the tree. Records purged by the licence / private-path rewrites left RAN_OK entries behind on this branch, and replay
then crashed (omega3 build: FileNotFoundError on mc-47a60db2...). Such an entry is QUARANTINED_*, so the call re-runs."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_no_ran_ok_entry_without_its_record():
    have = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "evidence", "model_calls", "**", "mc-*.json"),
                                                         recursive=True)}
    have |= {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "registry", "model_calls", "**", "mc-*.json"),
                                                          recursive=True)}
    bad = []
    for p in glob.glob(os.path.join(ROOT, "registry", "secondary_meta", "runs", "*.json")) + \
            glob.glob(os.path.join(ROOT, "registry", "model_proposals", "*runs*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for k, v in (d.items() if isinstance(d, dict) else []):
            if isinstance(v, dict) and v.get("state") == "RAN_OK" and v.get("record_id") and v["record_id"] not in have:
                bad.append(f"{os.path.basename(p)}: {k} -> {v['record_id']}")
    assert not bad, "RAN_OK entries whose record is not in the tree:\n" + "\n".join(bad)
