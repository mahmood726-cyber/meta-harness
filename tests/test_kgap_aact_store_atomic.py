"""PLANT: kgap.k_gap.AactStore.save() wrote the 20 MB store IN PLACE; two lanes' runs (a recount and a test pass) tore it
('Expecting , delimiter ... char 17484060', 6 Oct). A save that fails mid-write must leave the previous store intact,
and a completed save replaces the file whole (temp file + os.replace), like kgap.aact_adapter's index."""
import json
import os
import sys
from unittest.mock import patch

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402


def test_a_save_interrupted_mid_write_leaves_the_old_store_whole(tmp_path):
    p = tmp_path / "_aact_store.json"
    p.write_text(json.dumps({"pmid": {"1": ["NCT00000001"]}}), encoding="utf-8")
    s = k_gap.AactStore.__new__(k_gap.AactStore)
    s.path, s.d = str(p), {"pmid": {"1": ["NCT00000001"], "2": ["NCT00000002"]}}

    def torn(obj, fh, *a, **k):
        fh.write('{"pmid": {"1": ["NCT0')
        raise OSError("disk full mid-write")
    with patch.object(k_gap.json, "dump", torn), pytest.raises(OSError):
        s.save()
    assert json.loads(p.read_text(encoding="utf-8")) == {"pmid": {"1": ["NCT00000001"]}}
    assert not [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
    s.save()
    assert json.loads(p.read_text(encoding="utf-8"))["pmid"]["2"] == ["NCT00000002"]
