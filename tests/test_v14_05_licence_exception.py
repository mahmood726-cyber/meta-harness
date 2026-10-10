"""agy v14rec-r1-agy #1: the V14-05 stamp refuses a signature record missing its quote or its hex digests."""
import importlib.util
import json
import os

import pytest

_p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "v14_05_licence_exception.py")
_spec = importlib.util.spec_from_file_location("v14_05", _p)
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

GOOD = {"state": "SEEN_AND_SIGNED", "choice": "A", "quote": "sign v14", "packet_sha256": "a" * 64,
        "item_section_sha256": "b" * 64}


def _run(tmp_path, item):
    sig, lic = tmp_path / "sig.json", tmp_path / "lic.json"
    sig.write_text(json.dumps({"items": {"V14-05": item}}), encoding="utf-8")
    lic.write_text(json.dumps({"rows": [{"file": "f", "state": "RETAINED_CLAIM_DEPENDS"}, {"file": "g"}]}), encoding="utf-8")
    v.SIG, v.LIC = str(sig), str(lic)
    v.main()
    return json.loads(lic.read_text(encoding="utf-8"))["rows"]


def test_signed_item_stamps_retained_rows_only(tmp_path):
    rows = _run(tmp_path, GOOD)
    assert rows[0]["retained_exception"]["quote"] == "sign v14" and "retained_exception" not in rows[1]


@pytest.mark.parametrize("drop", ["quote", "packet_sha256", "item_section_sha256"])
def test_missing_evidence_refuses(tmp_path, drop):
    with pytest.raises(SystemExit):
        _run(tmp_path, {k: x for k, x in GOOD.items() if k != drop})


def test_non_hex_digest_refuses(tmp_path):
    with pytest.raises(SystemExit):
        _run(tmp_path, dict(GOOD, packet_sha256="not-a-digest"))
