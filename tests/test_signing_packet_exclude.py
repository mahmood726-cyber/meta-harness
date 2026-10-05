"""--exclude-packet: a notice already presented in a pending packet is never re-presented in a second one."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import signing_packet as sp  # noqa: E402


def test_PLANT_a_pending_packets_notices_are_not_re_presented(tmp_path):
    full = tmp_path / "full.md"
    sp.build(ROOT, "t", full, "", "VX")
    shas = sp.presented_in(full)
    assert shas                                                     # there are open notices to present
    first = tmp_path / "first.md"
    first.write_text("".join(f"`rendered_sha256 {s}`\n" for s in sorted(shas)[:1]), encoding="utf-8")
    second = tmp_path / "second.md"
    sp.build(ROOT, "t", second, "", "VY", [str(first)])
    assert sorted(shas)[0] not in sp.presented_in(second)          # the excluded one is gone
    assert sp.presented_in(second) == shas - {sorted(shas)[0]}      # and nothing else is
