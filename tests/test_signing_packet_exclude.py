"""--exclude-packet: a notice already presented in a pending packet is never re-presented in a second one."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import signing_packet as sp  # noqa: E402


def _root_with_open_notices(tmp_path, n=2):
    """A copy of the notice register with n notices re-OPENED (and their review files), so the plant never depends on
    whether the live register happens to hold open notices (6 Oct: every notice signed -> nothing to present)."""
    import json
    import shutil
    d = json.load(open(ROOT / "docs" / "result_changes.json", encoding="utf-8"))
    picked = [x for x in d["notices"] if x.get("slug") and (ROOT / "docs" / "reviews" / x["slug"] / "review.json").exists()][:n]
    for x in picked:
        x["reviewer_countersignature"] = {"state": "OPEN"}
    root = tmp_path / "root"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "result_changes.json").write_text(json.dumps({"notices": picked}), encoding="utf-8")
    for x in picked:
        dst = root / "docs" / "reviews" / x["slug"]
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "docs" / "reviews" / x["slug"] / "review.json", dst / "review.json")
    return root


def test_PLANT_a_pending_packets_notices_are_not_re_presented(tmp_path):
    root = _root_with_open_notices(tmp_path)
    full = tmp_path / "full.md"
    sp.build(root, "t", full, "", "VX")
    shas = sp.presented_in(full)
    assert shas                                                     # there are open notices to present
    first = tmp_path / "first.md"
    first.write_text("".join(f"`rendered_sha256 {s}`\n" for s in sorted(shas)[:1]), encoding="utf-8")
    second = tmp_path / "second.md"
    sp.build(root, "t", second, "", "VY", [str(first)])
    assert sorted(shas)[0] not in sp.presented_in(second)          # the excluded one is gone
    assert sp.presented_in(second) == shas - {sorted(shas)[0]}      # and nothing else is
