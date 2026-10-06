"""Plant (6 Oct, forest lane): fulltext_index.json is read-modify-written by several threads of one process (the per-trial
verifier at concurrency 5: copy_licence.pmc_licence and k_gap_counterfactual.pmc_fulltext_cached). Unlocked, threads
truncated each other's writes (JSONDecodeError 'Expecting value: line 1 column 1') and lost updates. One locked, atomic
update keeps every entry and never exposes a partial file."""
import json
import os
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import copy_licence as cl  # noqa: E402


def test_concurrent_updates_keep_every_entry_and_valid_json(tmp_path):
    p = str(tmp_path / "fulltext_index.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"0": {"copy_licence": "CC"}}, fh)

    def work(i):
        for j in range(15):
            cl.update_index(p, f"{i}-{j}", {"state": "HELD", "bytes": j})
    ts = [threading.Thread(target=work, args=(i,)) for i in range(8)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    idx = json.load(open(p, encoding="utf-8"))
    assert len(idx) == 1 + 8 * 15 and idx["0"] == {"copy_licence": "CC"}


def test_update_keeps_the_copy_licence_of_an_entry():
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "i.json")
    cl.update_index(p, "1", {"copy_licence": "CC", "copy_statement": "cc-by"})
    cl.update_index(p, "1", {"state": "HELD"}, replace=True)       # a full-entry replace still keeps copy_* fields
    assert json.load(open(p, encoding="utf-8"))["1"] == {"copy_licence": "CC", "copy_statement": "cc-by", "state": "HELD"}
